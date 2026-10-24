"""Offline anomaly detection for structured HTTP/application logs."""
from pathlib import Path
import re
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

FEATURES = ["status", "duration_ms", "bytes_sent", "hour", "is_error", "is_slow", "message_length"]
REQUIRED = ["timestamp", "level", "service", "status", "duration_ms", "bytes_sent", "message"]
LEVELS = {"DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"}

def prepare(df):
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Expected a pandas DataFrame")
    missing = [x for x in REQUIRED if x not in df.columns]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))
    if df.empty:
        raise ValueError("Log dataset is empty")
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce", utc=True)
    if out["timestamp"].isna().any():
        raise ValueError("One or more timestamps are invalid")
    for col in ["status", "duration_ms", "bytes_sent"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
        if out[col].isna().any() or (out[col]<0).any():
            raise ValueError(f"{col} must contain non-negative numbers")
    if (out["status"] > 599).any() or (out["status"] < 100).any():
        raise ValueError("status must be a valid HTTP status between 100 and 599")
    out["level"] = out["level"].fillna("").astype(str).str.upper()
    out["service"] = out["service"].fillna("").astype(str)
    out["message"] = out["message"].fillna("").astype(str)
    out["hour"] = out["timestamp"].dt.hour
    out["is_error"] = ((out["status"] >= 500) | out["level"].isin(["ERROR", "CRITICAL"])).astype(int)
    out["is_slow"] = (out["duration_ms"] > 1500).astype(int)
    out["message_length"] = out["message"].str.len()
    return out

def train_model(df, contamination=0.08, random_state=42):
    prepared = prepare(df)
    if len(prepared)<20:
        raise ValueError("Need at least 20 log rows to train")
    if not 0 < contamination <= .5:
        raise ValueError("contamination must be between 0 and 0.5")
    model=IsolationForest(n_estimators=120,contamination=contamination,random_state=random_state)
    model.fit(prepared[FEATURES].to_numpy(dtype=float))
    return model

def load_model(path):
    return joblib.load(path)  # Load only trusted local model files.

def analyze_logs(df, model):
    out=prepare(df)
    x=out[FEATURES].to_numpy(dtype=float)
    out["anomaly_score"] = np.round(-model.decision_function(x), 4)
    out["is_anomaly"] = model.predict(x)==-1
    def explanation(row):
        reasons=[]
        if row["status"]>=500: reasons.append("server error status")
        elif row["status"]>=400: reasons.append("client error status")
        if row["duration_ms"]>1500: reasons.append("slow response")
        if row["level"] in ["ERROR","CRITICAL"]: reasons.append("error severity")
        if not reasons: reasons.append("unusual combination of traffic features")
        return ", ".join(reasons)
    out["reason"] = out.apply(explanation,axis=1)
    out["timestamp"] = out["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out
