# initialize paths
from paths import dataDir

# Generated code starts here
# Import required libraries for data manipulation and numeric operations
import pandas as pd
import numpy as np

# Load the raw dataset from dataDir
rawData = pd.read_csv(dataDir / 'ibmchurn.csv')

# Drop the 'customerID' column as it is not predictive
rawData.drop(columns=['customerID'], inplace=True)

# Convert 'TotalCharges' to numeric, coercing errors to NaN, then fill NaN with 0
rawData['TotalCharges'] = pd.to_numeric(rawData['TotalCharges'], errors='coerce').fillna(0)

# Convert boolean 'Yes'/'No' columns to integer 1/0
boolCols = ['Partner', 'Dependents', 'PhoneService', 'PaperlessBilling', 'Churn']
for col in boolCols:
    rawData[col] = rawData[col].map({'Yes': 1, 'No': 0})

# Ensure 'SeniorCitizen' is integer type, convert if loaded as object
if rawData['SeniorCitizen'].dtype == object:
    rawData['SeniorCitizen'] = rawData['SeniorCitizen'].astype(int)

# Convert all boolean dtype columns to integer 1/0
bool_dtypes = rawData.select_dtypes(include=['bool']).columns
for col in bool_dtypes:
    rawData[col] = rawData[col].astype(int)

# Confirm 'Churn' exists, is numeric and has no NULLs
if 'Churn' not in rawData.columns:
    raise ValueError("Target column 'Churn' not found in dataset.")

if rawData['Churn'].isnull().any():
    raise ValueError("Target column 'Churn' contains NULL values.")

if not pd.api.types.is_numeric_dtype(rawData['Churn']):
    rawData['Churn'] = pd.to_numeric(rawData['Churn'], errors='raise')

# One-hot encode specified categorical columns with drop_first=True
catCols = ['gender', 'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
           'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
           'Contract', 'PaymentMethod']

rawData = pd.get_dummies(rawData, columns=catCols, drop_first=True)

# Ensure 'tenure' and 'MonthlyCharges' are numeric types
rawData['tenure'] = pd.to_numeric(rawData['tenure'], errors='coerce')
rawData['MonthlyCharges'] = pd.to_numeric(rawData['MonthlyCharges'], errors='coerce')

# Convert all remaining boolean type columns to int (True/False to 1/0)
bool_dtypes = rawData.select_dtypes(include=['bool']).columns
for col in bool_dtypes:
    rawData[col] = rawData[col].astype(int)

# Final check for object dtype columns (except target), raise error if any remain
nonNumericCols = rawData.select_dtypes(include=['object']).columns.tolist()
if nonNumericCols:
    raise ValueError(f"Non-numeric columns remain after processing: {nonNumericCols}")

# Save the processed DataFrame to dataDir with '_processed' appended to the filename stem
processedPath = dataDir / 'ibmchurn_processed.csv'
rawData.to_csv(processedPath, index=False)