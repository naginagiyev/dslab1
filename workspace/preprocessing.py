# initialize paths
from paths import dataDir

# Generated code starts here
# Import pandas and numpy for data manipulation and numeric operations
import pandas as pd
import numpy as np

# Load raw data from dataDir path
rawData = pd.read_csv(dataDir / 'ibmchurn.csv')

# Drop the 'customerID' column as it is an ID-like column without predictive value
dataNoId = rawData.drop(columns=['customerID'])

# Convert 'TotalCharges' to numeric, coerce errors to NaN, then fill NaN with 0
dataTotalChargesConverted = dataNoId.copy()
dataTotalChargesConverted['TotalCharges'] = pd.to_numeric(
    dataTotalChargesConverted['TotalCharges'], errors='coerce').fillna(0)

# Map 'Yes'/'No' to 1/0 for specific boolean columns
booleanColumns = ['Partner', 'Dependents', 'PhoneService', 'PaperlessBilling', 'Churn']
for col in booleanColumns:
    dataTotalChargesConverted[col] = dataTotalChargesConverted[col].map({'Yes': 1, 'No': 0})

# Convert any boolean dtype columns to integers
for col in dataTotalChargesConverted.select_dtypes(include='bool').columns:
    dataTotalChargesConverted[col] = dataTotalChargesConverted[col].astype(int)

# Ensure 'SeniorCitizen' is integer type if it loaded as object
if dataTotalChargesConverted['SeniorCitizen'].dtype == object:
    dataTotalChargesConverted['SeniorCitizen'] = dataTotalChargesConverted['SeniorCitizen'].astype(int)

# Add conversion of any remaining boolean columns in the entire dataset to int (including after mapping)
for col in dataTotalChargesConverted.columns:
    if dataTotalChargesConverted[col].dtype == bool:
        dataTotalChargesConverted[col] = dataTotalChargesConverted[col].astype(int)

# One-hot encode specified categorical columns with drop_first=True
categoricalCols = ['gender', 'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup', 
                   'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract', 
                   'PaymentMethod']
dataWithDummies = pd.get_dummies(dataTotalChargesConverted, columns=categoricalCols, drop_first=True)

# Convert any boolean dtype columns to integers after get_dummies (some pandas versions might create bool columns)
for col in dataWithDummies.select_dtypes(include='bool').columns:
    dataWithDummies[col] = dataWithDummies[col].astype(int)

# Confirm 'tenure' and 'MonthlyCharges' columns are numeric
dataWithDummies['tenure'] = pd.to_numeric(dataWithDummies['tenure'])
dataWithDummies['MonthlyCharges'] = pd.to_numeric(dataWithDummies['MonthlyCharges'])

# Verify that 'Churn' column exists, contains no null values, and is numeric
if 'Churn' not in dataWithDummies.columns:
    raise ValueError("Target column 'Churn' is missing from the dataset.")
if dataWithDummies['Churn'].isnull().any():
    raise ValueError("Target column 'Churn' contains null values.")

# Confirm there are no null values in any columns
if dataWithDummies.isnull().any().any():
    raise ValueError("Dataset contains null values.")

# Final check to ensure all features are numeric and no remaining object dtypes besides target
finalData = dataWithDummies.copy()
# All boolean columns already mapped; no categorical string columns remain

# Save the processed DataFrame to a new csv file in dataDir with '_processed' appended to filename stem
savePath = dataDir / 'ibmchurn_processed.csv'
finalData.to_csv(savePath, index=False)