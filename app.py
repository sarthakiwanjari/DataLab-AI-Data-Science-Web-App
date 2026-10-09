from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
import io
import json
from core.data_loader import load_dataset
from core.eda import dataset_profile, column_summary, correlation_data
from core.preprocessing import prepare_features
from core.classification import run_classification
from core.regression import run_regression
from core.clustering import run_clustering
from core.anomaly_detection import run_anomaly_detection
from core.report import build_report

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
ALLOWED_EXTENSIONS = {".csv"}

def get_uploaded_df(file):
    if not file or not file.filename:
        raise ValueError("Please choose a CSV file first.")
    if not file.filename.lower().endswith(".csv"):
        raise ValueError("For this starter version, please upload a CSV file.")
    return load_dataset(file)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/analyze")
def analyze():
    try:
        df = get_uploaded_df(request.files.get("file"))
        profile = dataset_profile(df)
        return jsonify({"ok": True, "profile": profile, "columns": list(df.columns),
                        "preview": df.head(8).replace({np.nan: None}).to_dict(orient="records"),
                        "summary": column_summary(df), "correlations": correlation_data(df)})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

@app.post("/api/ml")
def machine_learning():
    try:
        df = get_uploaded_df(request.files.get("file"))
        task = request.form.get("task", "classification")
        target = request.form.get("target", "")
        if task == "classification":
            result = run_classification(df, target)
        elif task == "regression":
            result = run_regression(df, target)
        elif task == "clustering":
            result = run_clustering(df, int(request.form.get("clusters", 3)))
        elif task == "anomaly":
            result = run_anomaly_detection(df)
        else:
            raise ValueError("Choose a supported ML task.")
        return jsonify({"ok": True, "result": result})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

@app.post("/api/report")
def report():
    try:
        df = get_uploaded_df(request.files.get("file"))
        report_text = build_report(df)
        return send_file(io.BytesIO(report_text.encode("utf-8")), mimetype="text/plain",
                         as_attachment=True, download_name="datalab-analysis-report.txt")
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
