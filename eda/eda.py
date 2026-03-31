import csv
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from readers import readers as externalReaders

class EDA:
    def __init__(self, datasetPath: str):
        self.datasetPath = datasetPath
        # map to get file extensions
        self.readers = {**externalReaders,
                        '.csv': self.readDelimited,
                        '.tsv': self.readDelimited,
                        '.txt': self.readDelimited,
                        '.data': self.readDelimited}
        # load data
        self.data = self.loadData().copy()
        # infer types
        self.typeMap = self.inferTypes()
    
    # read delimited data
    # find the seperator used in dataset to prevent seperator related errors
    def readDelimited(self, sampleSize=4096):
        try:
            with open(self.datasetPath, 'r', encoding='utf-8') as f:
                sample = f.read(sampleSize)
                delimiter = csv.Sniffer().sniff(sample).delimiter
        except Exception:
            delimiter = ','
        try:
            return pd.read_csv(self.datasetPath, delimiter=delimiter, encoding='utf-8', low_memory=False)
        except UnicodeDecodeError:
            return pd.read_csv(self.datasetPath, delimiter=delimiter, encoding='latin-1', low_memory=False)

    # load data
    def loadData(self):
        ext = Path(self.datasetPath).suffix.lower()
        reader = self.readers.get(ext)
        if not reader:
            raise ValueError(f"Unsupported file format: {ext}")
        return reader()

    # infer types of the columns in the dataset
    def inferTypes(self) -> dict[str, str]:
        df = self.data
        nRows = len(df)
        typeMap: dict[str, str] = {}
        typeWarnings: dict[str, list[str]] = {}

        for colName in df.columns:
            col = df[colName]
            columnWarnings: list[str] = []

            # check if the column is entirely null
            if col.isna().all():
                typeMap[colName] = "unknown"
                columnWarnings.append("Column is entirely null.")
                typeWarnings[colName] = columnWarnings
                continue

            # check if the column is a constant column (only one unique value)
            nunique = col.nunique(dropna=True)
            if nunique == 1:
                typeMap[colName] = "constant"
                columnWarnings.append("Constant column — safe to drop.")
                typeWarnings[colName] = columnWarnings
                continue

            # check if the column is an id-like column (more than 95% of the values are unique)
            uniqueRatio = nunique / nRows if nRows > 0 else 0.0
            if nRows >= 50 and uniqueRatio > 0.95:
                typeMap[colName] = "id_like"
                typeWarnings[colName] = columnWarnings
                continue

            if pd.api.types.is_bool_dtype(col.dtype):
                typeMap[colName] = "boolean"
                typeWarnings[colName] = columnWarnings
                continue

            if pd.api.types.is_datetime64_any_dtype(col.dtype):
                typeMap[colName] = "datetime"
                typeWarnings[colName] = columnWarnings
                continue

            if pd.api.types.is_object_dtype(col.dtype):
                nonNull = col.dropna()

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=UserWarning)
                    try:
                        parsedDt = pd.to_datetime(nonNull, errors="coerce", format="mixed")
                    except TypeError:
                        parsedDt = pd.to_datetime(nonNull, errors="coerce")
                natRate = parsedDt.isna().mean() if len(nonNull) > 0 else 1.0
                if natRate < 0.10:
                    inferred = "datetime"
                else:
                    textValues = nonNull.astype(str).str.strip()
                    if len(textValues) > 0:
                        avgWordCount = textValues.str.split().str.len().mean()
                    else:
                        avgWordCount = 0.0

                    if avgWordCount > 3:
                        inferred = "text"
                    elif nunique == 2:
                        inferred = "boolean"
                    else:
                        inferred = "categorical"

                cleanedNumeric = (
                    nonNull.astype(str)
                    .str.replace(",", "", regex=False)
                    .str.replace("$", "", regex=False)
                    .str.strip()
                )
                numericCast = pd.to_numeric(cleanedNumeric, errors="coerce")
                numericSuccess = numericCast.notna().mean() if len(nonNull) > 0 else 0.0
                if numericSuccess > 0.80:
                    columnWarnings.append(
                        "Column appears numeric but is stored as string — consider converting."
                    )

                if nonNull.map(type).nunique() > 1:
                    columnWarnings.append("Mixed types detected in this column.")

                typeMap[colName] = inferred
                typeWarnings[colName] = columnWarnings
                continue

            isInteger = False
            isFloat = False
            try:
                npDtype = np.dtype(col.dtype)
                isInteger = np.issubdtype(npDtype, np.integer)
                isFloat = np.issubdtype(npDtype, np.floating)
            except TypeError:
                isInteger = pd.api.types.is_integer_dtype(col.dtype)
                isFloat = pd.api.types.is_float_dtype(col.dtype)

            if isInteger or isFloat:
                if nunique == 2:
                    inferred = "boolean"
                elif isFloat or nunique > 20:
                    inferred = "numeric_continuous"
                else:
                    inferred = "numeric_discrete"

                typeMap[colName] = inferred
                typeWarnings[colName] = columnWarnings
                continue

            typeMap[colName] = "categorical"
            typeWarnings[colName] = columnWarnings

        self.typeMap = typeMap
        self.typeWarnings = typeWarnings
        return typeMap

if __name__ == "__main__":
    eda = EDA("data/ibmchurn.csv")
    print(eda.typeMap)