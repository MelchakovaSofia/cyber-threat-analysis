from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.auth.deps import get_current_user
from app.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import RefreshRequest, TokenPair, UserCreate, UserLogin, UserOut
from app.utils.logger import get_logger

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger(__name__)


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        logger.info(f"Registration attempt for login: {payload.login}")
        
        exists = db.query(User).filter(
            (User.login == payload.login) | (User.email == payload.email)
        ).first()
        if exists:
            logger.warning(f"Registration failed: login or email already exists - {payload.login}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Login or email already registered"
            )
        
        user = User(
            login=payload.login,
            email=payload.email,
            password=hash_password(payload.password),
            role=payload.role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User registered successfully: {user.login} with role {user.role.value}")
        return user
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during registration: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during registration"
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration"
        )


@router.post("/login", response_model=TokenPair)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return tokens."""
    try:
        logger.info(f"Login attempt for login: {payload.login}")
        
        user = db.query(User).filter(User.login == payload.login).first()
        if not user or not verify_password(payload.password, user.password):
            logger.warning(f"Login failed: invalid credentials for {payload.login}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid credentials"
            )
        
        tokens = TokenPair(
            access_token=create_access_token(user.login, user.role.value),
            refresh_token=create_refresh_token(user.login, user.role.value),
        )
        
        logger.info(f"User logged in successfully: {user.login}")
        return tokens
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error during login: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during login"
        )
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest):
    """Refresh access token using refresh token."""
    try:
        logger.debug("Token refresh attempt")
        
        try:
            data = decode_token(payload.refresh_token)
        except ValueError as e:
            logger.warning(f"Token refresh failed: invalid refresh token - {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid refresh token"
            )
        
        if data.get("type") != "refresh":
            logger.warning("Token refresh failed: wrong token type")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid refresh token"
            )
        
        tokens = TokenPair(
            access_token=create_access_token(data["sub"], data["role"]),
            refresh_token=create_refresh_token(data["sub"], data["role"]),
        )
        
        logger.info(f"Token refreshed successfully for user: {data['sub']}")
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during token refresh"
        )


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    """Get current user information."""
    try:
        logger.debug(f"User info requested for: {user.login}")
        return user
    except Exception as e:
        logger.error(f"Error fetching user info: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user information"
        )
