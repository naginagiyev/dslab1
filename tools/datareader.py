import csv
import pandas as pd
from pathlib import Path
from configuration.edaconfig import readers as externalReaders

def readDelimited(inputPath: str, sampleSize: int = 4096) -> pd.DataFrame:
    delimiter = None
    ext = Path(inputPath).suffix.lower()

    if ext == ".tsv":
        delimiter = "\t"
    else:
        try:
            with open(inputPath, "r", encoding="utf-8") as file:
                sample = file.read(sampleSize)
                delimiter = csv.Sniffer().sniff(sample).delimiter
        except Exception:
            delimiter = None

    readKwargs = {"engine": "python", "sep": delimiter if delimiter is not None else None}
    try:
        return pd.read_csv(inputPath, encoding="utf-8", **readKwargs)
    except UnicodeDecodeError:
        return pd.read_csv(inputPath, encoding="latin-1", **readKwargs)

def loadData(inputPath: str, targetCol: str) -> pd.DataFrame:
    ext = Path(inputPath).suffix.lower()
    df: pd.DataFrame | None = None

    if ext in {".csv", ".tsv"}:
        df = readDelimited(inputPath)
    elif ext in externalReaders:
        df = externalReaders[ext](inputPath)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

    if df is None or df.empty:
        raise ValueError("Loaded dataframe is empty.")

    if df.shape[1] == 0:
        raise ValueError("Loaded dataframe has no columns.")

    if all(df[col].isna().all() for col in df.columns):
        raise ValueError("All columns are fully missing.")

    if targetCol not in df.columns:
        raise ValueError(f"Target column '{targetCol}' was not found in the dataset.")

    return df