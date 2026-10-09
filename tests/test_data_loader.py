import io
from core.data_loader import load_dataset

def test_load_csv():
    df = load_dataset(io.BytesIO(b"a,b\n1,2\n3,4\n"))
    assert df.shape == (2, 2)
    assert list(df.columns) == ["a", "b"]
