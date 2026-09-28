import os
from pathlib import Path
from typing import List, Union

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_ml_model_dir() -> str:
    project_root = Path(__file__).resolve().parents[2]
    return str((project_root / "ml_models").resolve())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Intelligent Cyber Threat Analysis System"
    database_url: str = "postgresql+psycopg2://cta:cta_password@localhost:5432/cta_db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    ml_model_dir: str = "ml_models"

    @field_validator('ml_model_dir', mode='before')
    @classmethod
    def resolve_ml_model_dir(cls, v: Union[str, None]) -> str:
        """Use a writable project-local directory when environment sets /app or another invalid target."""
        candidate = (v or "").strip()
        if not candidate:
            return _default_ml_model_dir()

        path = Path(candidate)
        if not path.is_absolute():
            path = (Path(__file__).resolve().parents[2] / candidate).resolve()

        if str(path).startswith("/app") or not os.access(str(path.parent if path.parent.exists() else path), os.W_OK):
            return _default_ml_model_dir()

        return str(path)
    
    # Security settings
    environment: str = "development"  # development, staging, production
    allowed_origins: Union[str, List[str]] = "*"  # CORS allowed origins (string or list)
    allowed_methods: Union[str, List[str]] = "*"  # CORS allowed methods (string or list)
    allowed_headers: Union[str, List[str]] = "*"  # CORS allowed headers (string or list)
    allow_credentials: bool = True  # CORS allow credentials
    
    # Rate limiting (basic implementation)
    rate_limit_requests: int = 100  # requests per minute
    rate_limit_period: int = 60  # seconds

    @field_validator('allowed_origins', 'allowed_methods', 'allowed_headers', mode='before')
    @classmethod
    def parse_cors_list(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS settings from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid_environments = ['development', 'staging', 'production']
        if v.lower() not in valid_environments:
            raise ValueError(f'Environment must be one of: {", ".join(valid_environments)}')
        return v.lower()

    @model_validator(mode='after')
    def validate_security_settings(self) -> 'Settings':
        """Validate security settings based on environment."""
        env = self.environment
        
        # Validate secret key in production
        if env == 'production':
            if self.secret_key in ['change-me-in-production', 'test-secret']:
                raise ValueError(
                    'Secret key must be changed in production. '
                    'Generate a strong key using: openssl rand -base64 32'
                )
            if len(self.secret_key) < 32:
                raise ValueError('Secret key must be at least 32 characters long in production')
            
            # Warn about wildcard CORS in production
            if '*' in self.allowed_origins:
                import warnings
                warnings.warn(
                    'Wildcard CORS origin (*) is not recommended in production. '
                    'Specify exact domains in ALLOWED_ORIGINS environment variable.'
                )
        
        return self

settings = Settings()
