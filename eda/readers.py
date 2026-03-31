import pandas as pd

readers = {
    '.xlsx': pd.read_excel,
    '.xls': pd.read_excel,
    '.json': pd.read_json,
    '.parquet': pd.read_parquet,
    '.pkl': pd.read_pickle,
    '.pickle': pd.read_pickle,
    '.feather': pd.read_feather,
    '.orc': pd.read_orc,
    '.h5': pd.read_hdf,
    '.hdf5': pd.read_hdf,
    '.xml': pd.read_xml,
}