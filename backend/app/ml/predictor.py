"""Loading a trained model and scoring network logs."""
from collections import Counter

import joblib
import numpy as np
import pandas as pd

from app.ml.features import build_features

SEVERITY_THRESHOLDS = ((0.85, "critical"), (0.65, "high"), (0.4, "medium"))


def load_model(path: str):
    return joblib.load(path)


def severity_from_probability(probability: float) -> str:
    for threshold, level in SEVERITY_THRESHOLDS:
        if probability >= threshold:
            return level
    return "low"


def predict(model, df: pd.DataFrame) -> list[dict]:
    features = build_features(df)
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)[:, 1]
    else:
        raw = np.asarray(model.predict(features))
        unique = set(np.unique(raw).tolist())
        if unique <= {-1, 1}:
            probabilities = [1.0 if value == -1 else 0.0 for value in raw]
        else:
            counts = Counter(raw.tolist())
            anomaly = min(counts, key=counts.get)
            probabilities = [1.0 if value == anomaly else 0.0 for value in raw]

    results = []
    for log_id, probability in zip(df["id"], probabilities):
        probability = float(probability)
        results.append(
            {
                "log_id": int(log_id),
                "threat_type": "anomaly" if probability >= 0.5 else "normal",
                "probability": round(probability, 4),
                "severity": severity_from_probability(probability),
            }
        )
    return results
