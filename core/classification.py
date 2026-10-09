import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from core.preprocessing import prepare_features

def run_classification(df, target):
    if not target or target not in df.columns:
        raise ValueError("Select a valid target column for classification.")
    data = df.dropna(subset=[target]).copy()
    if data[target].nunique() < 2:
        raise ValueError("Classification needs at least two target classes.")
    if data[target].nunique() > 30:
        raise ValueError("The selected target has more than 30 classes. Try another target or use regression.")
    X = data.drop(columns=[target])
    y = data[target].astype(str)
    if X.empty:
        raise ValueError("The dataset needs at least one feature besides the target.")
    if len(data) < 12:
        raise ValueError("Please upload at least 12 labelled rows for a train/test evaluation.")
    stratify = y if y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=stratify
    )
    prep, _, _ = prepare_features(X_train)
    model = Pipeline([("preprocess", prep), ("model", RandomForestClassifier(
        n_estimators=150, random_state=42, class_weight="balanced"
    ))])
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    labels = sorted(y.unique().tolist())
    cm = confusion_matrix(y_test, pred, labels=labels)
    return {
        "task": "Classification", "algorithm": "Random Forest Classifier",
        "target": str(target), "train_rows": int(len(X_train)), "test_rows": int(len(X_test)),
        "metrics": {
            "accuracy": round(float(accuracy_score(y_test, pred)), 4),
            "precision_weighted": round(float(precision_score(y_test, pred, average="weighted", zero_division=0)), 4),
            "recall_weighted": round(float(recall_score(y_test, pred, average="weighted", zero_division=0)), 4),
            "f1_weighted": round(float(f1_score(y_test, pred, average="weighted", zero_division=0)), 4)
        },
        "confusion_matrix": cm.tolist(), "labels": labels,
        "note": "Metrics are measured on a held-out test split. Small or imbalanced datasets can produce unstable estimates."
    }
