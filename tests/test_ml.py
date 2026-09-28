import numpy as np
import pandas as pd

from app.ml.features import FEATURE_COLUMNS, build_features
from app.ml.predictor import severity_from_probability
from app.ml.trainer import train_model


def sample_dataframe(rows: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    return pd.DataFrame(
        {
            "id": range(rows),
            "ip_address": [f"10.0.0.{i % 20}" for i in range(rows)],
            "timestamp": pd.date_range("2026-09-01", periods=rows, freq="min"),
            "protocol": rng.choice(["TCP", "UDP", "HTTP"], rows),
            "port": rng.integers(20, 9000, rows),
            "bytes_sent": rng.integers(0, 50000, rows),
            "bytes_received": rng.integers(0, 50000, rows),
            "status": rng.choice(["ok", "failed"], rows),
            "label": rng.integers(0, 2, rows),
        }
    )


def test_build_features_columns():
    features = build_features(sample_dataframe())
    assert list(features.columns) == FEATURE_COLUMNS


def test_train_random_forest():
    metrics = train_model(sample_dataframe(), "random_forest")
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert metrics["model_name"] == "random_forest"


def test_train_isolation_forest():
    metrics = train_model(sample_dataframe(), "isolation_forest")
    assert metrics["version"]


def test_train_from_status_without_label_column():
    df = sample_dataframe()
    df = df.drop(columns=["label"])
    metrics = train_model(df, "decision_tree")
    assert metrics["model_name"] == "decision_tree"
    assert 0.0 <= metrics["accuracy"] <= 1.0


def test_severity_levels():
    assert severity_from_probability(0.9) == "critical"
    assert severity_from_probability(0.1) == "low"
