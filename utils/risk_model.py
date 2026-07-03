import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

MODEL_PATH = "sample_data/risk_model.pkl"

WEATHER_MAP  = {"clear": 0, "Clear": 0, "fog": 1, "Foggy": 1, "Hazy": 1,
                "rain": 2, "Rainy": 2, "Stormy": 3}
ROAD_MAP     = {"rural": 0, "Village Road": 0, "urban": 1, "Urban Road": 1,
                "State Highway": 2, "highway": 3, "National Highway": 3}
DENSITY_MAP  = {"low": 0, "medium": 1, "high": 2}
VISIBILITY_MAP = {"high": 0, "medium": 1, "low": 2}


def _encode(df: pd.DataFrame) -> np.ndarray:
    d = df.copy()
    d["weather"]         = d.get("weather", pd.Series(["clear"]*len(d))).map(WEATHER_MAP).fillna(0)
    d["road_type"]       = d.get("road_type", pd.Series(["urban"]*len(d))).map(ROAD_MAP).fillna(1)
    d["traffic_density"] = d.get("traffic_density", pd.Series(["medium"]*len(d))).map(DENSITY_MAP).fillna(1)
    d["visibility"]      = d.get("visibility", pd.Series(["high"]*len(d))).map(VISIBILITY_MAP).fillna(0)
    cols = ["latitude","longitude","hour","weather","road_type",
            "traffic_density","visibility","is_peak_hour",
            "vehicles_involved","risk_score"]
    for c in cols:
        if c not in d.columns:
            d[c] = 0
    return d[cols].fillna(0).values


def train_model(df: pd.DataFrame):
    df = df.copy()
    # label: severity >= 2 (major or fatal) → high risk
    y = (df["severity"] >= 2).astype(int)
    if y.nunique() < 2:
        y = (np.arange(len(y)) % 2).astype(int)
    X = _encode(df)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    clf = RandomForestClassifier(
        n_estimators=200, max_depth=12,
        random_state=42, class_weight="balanced", n_jobs=-1
    )
    clf.fit(X_tr, y_tr)
    os.makedirs("sample_data", exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    acc = clf.score(X_te, y_te)
    return clf, acc


def load_or_train(df: pd.DataFrame):
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    clf, _ = train_model(df)
    return clf


def predict_risk(clf, row: dict) -> float:
    """Return risk probability 0–1 for a single point."""
    df = pd.DataFrame([row])
    X  = _encode(df)
    return float(clf.predict_proba(X)[0][1])
