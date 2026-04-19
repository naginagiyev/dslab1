# initialize paths
from paths import dataDir
from paths import sandboxDir

# Generated code starts here
from pathlib import Path
import pandas as pd
import numpy as np

# load raw data
filename = 'ibmchurn.csv'
filePath = dataDir / filename
dfRaw = pd.read_csv(filePath)

# drop unneeded identifier column
dfRaw = dfRaw.drop(columns=['customerID'])

# convert 'TotalCharges' to numeric, coerce errors to NaN
dfRaw['TotalCharges'] = pd.to_numeric(dfRaw['TotalCharges'], errors='coerce')

# impute missing 'TotalCharges' with median of the column
medianTotalCharges = dfRaw['TotalCharges'].median()
dfRaw['TotalCharges'] = dfRaw['TotalCharges'].fillna(medianTotalCharges)

# encode boolean columns with Yes/No to 1/0
boolCols = ['Partner', 'Dependents', 'PhoneService', 'PaperlessBilling', 'Churn']
for col in boolCols:
    dfRaw[col] = dfRaw[col].map({'Yes': 1, 'No': 0})

# 'SeniorCitizen' already numeric 0 or 1, leave as is

# convert any remaining boolean columns to int (like after mapping)
if dfRaw.select_dtypes(include=['bool']).shape[1] > 0:
    bool_columns = dfRaw.select_dtypes(include=['bool']).columns
    dfRaw[bool_columns] = dfRaw[bool_columns].astype(int)

# Ensure no nulls in 'Churn' column
if 'Churn' in dfRaw.columns:
    if dfRaw['Churn'].isnull().any():
        dfRaw['Churn'] = dfRaw['Churn'].fillna(0)
    dfRaw['Churn'] = dfRaw['Churn'].astype(int)

# ensure there are no null values in any columns
dfRaw = dfRaw.fillna(method='ffill').fillna(method='bfill')

# convert all boolean columns to integer type (to make sure after fillna)
bool_columns = dfRaw.select_dtypes(include=['bool']).columns
if len(bool_columns) > 0:
    dfRaw[bool_columns] = dfRaw[bool_columns].astype(int)

# Convert any remaining boolean columns to integer type again to be sure
bool_columns = dfRaw.select_dtypes(include='bool').columns
if len(bool_columns) > 0:
    dfRaw[bool_columns] = dfRaw[bool_columns].astype(int)

# Confirm there are no NULL values in the dataset
assert not dfRaw.isnull().any().any(), "There are still null values in the dataset."

# Confirm the target column 'Churn' is present and numeric
assert 'Churn' in dfRaw.columns, "'Churn' column is missing from the dataset."
assert pd.api.types.is_numeric_dtype(dfRaw['Churn']), "'Churn' column is not numeric."

# one-hot encode categorical columns with drop_first=True to avoid collinearity
oneHotCols = ['gender', 'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
              'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract', 'PaymentMethod']
dfProcessed = pd.get_dummies(dfRaw, columns=oneHotCols, drop_first=True)

# scale numeric columns using standardization (z-score)
numCols = ['tenure', 'MonthlyCharges', 'TotalCharges']
for col in numCols:
    meanVal = dfProcessed[col].mean()
    stdVal = dfProcessed[col].std()
    dfProcessed[col] = (dfProcessed[col] - meanVal) / stdVal

# save processed dataframe with '_processed' appended before extension
newFileName = filename.replace('.csv', '_processed.csv')
savePath = dataDir / newFileName
dfProcessed.to_csv(savePath, index=False)