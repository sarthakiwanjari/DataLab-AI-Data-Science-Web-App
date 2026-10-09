from core.eda import dataset_profile, column_summary

def build_report(df):
    p = dataset_profile(df)
    lines = [
        "DATALAB AI — DATASET ANALYSIS REPORT",
        "=" * 42, "",
        f"Rows: {p['rows']}",
        f"Columns: {p['columns']}",
        f"Missing cells: {p['missing']}",
        f"Duplicate rows: {p['duplicates']}",
        f"Numeric columns: {p['numeric_columns']}",
        f"Categorical columns: {p['categorical_columns']}",
        f"Approximate memory: {p['memory_kb']} KB", "",
        "COLUMN SUMMARY", "-" * 42
    ]
    for c in column_summary(df):
        lines.append(f"{c['name']} | type={c['dtype']} | missing={c['missing']} | unique={c['unique']}")
        if c.get("mean") is not None:
            lines.append(f"  mean={c['mean']} | min={c['min']} | max={c['max']}")
        elif c.get("top_value") is not None:
            lines.append(f"  most common value={c['top_value']}")
    lines += ["", "Interpretation note: statistics describe the uploaded data and do not establish causation."]
    return "\\n".join(lines)
