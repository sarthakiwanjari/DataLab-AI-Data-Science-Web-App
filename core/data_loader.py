import pandas as pd

def load_dataset(file):
    """Load a CSV upload and apply conservative size/shape checks."""
    df = pd.read_csv(file)
    if df.empty:
        raise ValueError("The uploaded CSV is empty.")
    if len(df.columns) < 1:
        raise ValueError("No columns were found in the uploaded CSV.")
    if len(df) > 100_000:
        raise ValueError("This demo supports up to 100,000 rows per upload.")
    if len(df.columns) > 150:
        raise ValueError("This demo supports up to 150 columns per upload.")
    df.columns = [str(c).strip() or f"column_{i+1}" for i, c in enumerate(df.columns)]
    return df
