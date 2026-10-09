import pandas as pd
from sklearn.ensemble import IsolationForest
from core.preprocessing import prepare_features

def run_anomaly_detection(df):
    data = df.dropna(axis=1, how="all").copy()
    if len(data) < 10:
        raise ValueError("Please upload at least 10 rows for anomaly detection.")
    prep, _, _ = prepare_features(data)
    X = prep.fit_transform(data)
    model = IsolationForest(contamination="auto", random_state=42, n_estimators=150)
    labels = model.fit_predict(X)
    scores = model.decision_function(X)
    result = data.head(200).copy()
    result["anomaly_flag"] = ["Anomaly" if x == -1 else "Typical" for x in labels[:200]]
    result["anomaly_score"] = [round(float(x), 5) for x in scores[:200]]
    return {
        "task": "Anomaly Detection", "algorithm": "Isolation Forest",
        "rows_analyzed": int(len(data)), "anomalies_detected": int((labels == -1).sum()),
        "anomaly_percentage": round(float((labels == -1).mean() * 100), 2),
        "preview": result.astype(object).where(pd.notna(result), None).to_dict(orient="records"),
        "note": "Anomalies are unusual relative to this dataset; they are not automatically errors or fraud."
    }
