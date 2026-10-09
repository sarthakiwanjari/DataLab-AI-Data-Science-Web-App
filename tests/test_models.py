import pandas as pd
from core.classification import run_classification
from core.regression import run_regression
from core.clustering import run_clustering
from core.anomaly_detection import run_anomaly_detection

def test_classification():
    df = pd.DataFrame({
        "x": list(range(40)),
        "kind": ["A" if i % 2 == 0 else "B" for i in range(40)]
    })
    result = run_classification(df, "kind")
    assert "accuracy" in result["metrics"]

def test_regression():
    df = pd.DataFrame({"x": list(range(40)), "y": [i * 2.0 for i in range(40)]})
    result = run_regression(df, "y")
    assert "mae" in result["metrics"]

def test_clustering():
    df = pd.DataFrame({"x": list(range(30)), "y": [i % 3 for i in range(30)]})
    result = run_clustering(df, 3)
    assert result["clusters"] == 3

def test_anomaly():
    df = pd.DataFrame({"x": list(range(30)), "y": [i % 5 for i in range(30)]})
    result = run_anomaly_detection(df)
    assert "anomalies_detected" in result
