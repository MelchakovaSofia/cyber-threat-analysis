"""Model training: supervised classifiers and unsupervised anomaly detection."""
import os
from datetime import datetime, timezone

import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from app.config import settings
from app.ml.features import build_features

SUPERVISED = {
    "random_forest": lambda: RandomForestClassifier(n_estimators=200, random_state=42),
    "decision_tree": lambda: DecisionTreeClassifier(random_state=42),
    "logistic_regression": lambda: LogisticRegression(max_iter=1000),
}

UNSUPERVISED = {
    "isolation_forest": lambda: IsolationForest(contamination=0.05, random_state=42),
    "kmeans": lambda: KMeans(n_clusters=2, n_init=10, random_state=42),
}

THREAT_STATUSES = {"failed", "denied", "error", "malicious", "blocked"}


def _resolve_labels(df: pd.DataFrame) -> pd.Series:
    """Use explicit labels when present; otherwise derive them from event status."""
    if "label" in df.columns and df["label"].notna().any():
        y = df["label"].fillna(0).astype(int)
    else:
        y = df["status"].astype(str).str.lower().isin(THREAT_STATUSES).astype(int)
    if y.nunique() < 2:
        raise ValueError(
            "Supervised training needs both normal and threat examples. "
            "Import a labeled CSV or train isolation_forest / kmeans instead."
        )
    return y


def train_model(df: pd.DataFrame, model_name: str = "random_forest", test_size: float = 0.2) -> dict:
    """Train a model and persist it with joblib. Returns metrics."""
    features = build_features(df)
    os.makedirs(settings.ml_model_dir, exist_ok=True)
    version = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    path = os.path.join(settings.ml_model_dir, f"{model_name}_{version}.joblib")

    if model_name in UNSUPERVISED:
        model = UNSUPERVISED[model_name]()
        model.fit(features)
        joblib.dump(model, path)
        return {
            "model_name": model_name,
            "version": version,
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "path": path,
        }

    if model_name not in SUPERVISED:
        raise ValueError(f"Unknown model: {model_name}")

    y = _resolve_labels(df)
    x_train, x_test, y_train, y_test = train_test_split(
        features, y, test_size=test_size, random_state=42, stratify=y
    )
    model = SUPERVISED[model_name]()
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    joblib.dump(model, path)
    return {
        "model_name": model_name,
        "version": version,
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "path": path,
    }
