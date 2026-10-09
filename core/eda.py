import pandas as pd
import numpy as np

def _json_safe(value):
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value

def dataset_profile(df):
    numeric = df.select_dtypes(include="number")
    missing = int(df.isna().sum().sum())
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing": missing,
        "duplicates": int(df.duplicated().sum()),
        "numeric_columns": int(len(numeric.columns)),
        "categorical_columns": int(df.shape[1] - len(numeric.columns)),
        "memory_kb": round(float(df.memory_usage(deep=True).sum()) / 1024, 1),
        "missing_pct": round(missing / max(df.size, 1) * 100, 2)
    }

def column_summary(df):
    output = []
    for col in df.columns:
        s = df[col]
        item = {
            "name": str(col),
            "dtype": str(s.dtype),
            "missing": int(s.isna().sum()),
            "unique": int(s.nunique(dropna=True))
        }
        if pd.api.types.is_numeric_dtype(s):
            clean = s.dropna()
            item.update({
                "mean": _json_safe(round(float(clean.mean()), 4)) if len(clean) else None,
                "min": _json_safe(clean.min()) if len(clean) else None,
                "max": _json_safe(clean.max()) if len(clean) else None
            })
        else:
            top = s.dropna().astype(str).value_counts().head(1)
            item["top_value"] = top.index[0] if len(top) else None
        output.append(item)
    return output

def correlation_data(df):
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        return {"labels": [], "values": []}
    corr = numeric.corr(numeric_only=True).round(3).replace({np.nan: None})
    return {"labels": [str(c) for c in corr.columns],
            "values": corr.values.tolist()}
