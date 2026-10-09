import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from core.preprocessing import prepare_features

def run_regression(df, target):
    if not target or target not in df.columns:
        raise ValueError("Select a valid numeric target column for regression.")
    if not pd.api.types.is_numeric_dtype(df[target]):
        raise ValueError("Regression target must be numeric.")
    data = df.dropna(subset=[target]).copy()
    X = data.drop(columns=[target])
    y = data[target]
    if X.empty:
        raise ValueError("The dataset needs at least one feature besides the target.")
    if len(data) < 12:
        raise ValueError("Please upload at least 12 rows for a train/test evaluation.")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    prep, _, _ = prepare_features(X_train)
    model = Pipeline([("preprocess", prep), ("model", RandomForestRegressor(
        n_estimators=150, random_state=42, n_jobs=-1
    ))])
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    return {
        "task": "Regression", "algorithm": "Random Forest Regressor", "target": str(target),
        "train_rows": int(len(X_train)), "test_rows": int(len(X_test)),
        "metrics": {
            "mae": round(float(mean_absolute_error(y_test, pred)), 4),
            "rmse": round(float(mean_squared_error(y_test, pred) ** 0.5), 4),
            "r2": round(float(r2_score(y_test, pred)), 4) if len(y_test) > 1 else None
        },
        "note": "Metrics are measured on a held-out test split. R² can be negative when predictions are worse than a mean baseline."
    }
