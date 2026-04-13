# initialize paths
from paths import dataDir

# Generated code starts here
# Import necessary libraries for data manipulation and numeric operations
import pandas as pd
import numpy as np

# Load raw dataset from the given data directory
rawData = pd.read_csv(dataDir / "ibmchurn.csv")

# Data transformation: Drop unique identifier column
rawData.drop(columns=["customerID"], inplace=True)

# Convert 'Yes'/'No' columns to integer 1/0
boolCols = ['Partner', 'Dependents', 'PhoneService', 'PaperlessBilling', 'Churn']
for col in boolCols:
    rawData[col] = rawData[col].map({'Yes': 1, 'No': 0}).astype(int)

# Ensure 'SeniorCitizen' is integer type
rawData['SeniorCitizen'] = rawData['SeniorCitizen'].astype(int)

# Convert 'TotalCharges' to numeric, coerce errors to NaN and fill NaN with 0.0
rawData['TotalCharges'] = pd.to_numeric(rawData['TotalCharges'], errors='coerce').fillna(0.0)

# One-hot encode categorical columns with 3 or more uniques, drop first to avoid multicollinearity
categoricalCols = ['gender', 'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
                   'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
                   'Contract', 'PaymentMethod']
rawData = pd.get_dummies(rawData, columns=categoricalCols, drop_first=True)

# Convert all boolean columns to integers
bool_dtypes = rawData.select_dtypes(include=['bool']).columns
rawData[bool_dtypes] = rawData[bool_dtypes].astype(int)

# Save the processed DataFrame to the specified path
rawData.to_csv(dataDir / "ibmchurn_processed.csv", index=False)