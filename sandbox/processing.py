# initialize paths
from paths import dataDir
from paths import workspaceDir

# Generated code starts here
import pandas as pd
import numpy as np

# Load data
data = pd.read_csv(dataDir / 'ibmchurn.csv')

# Drop 'customerID' column
data = data.drop(columns=['customerID'])

# Clean and convert 'TotalCharges' column
data['TotalCharges'] = data['TotalCharges'].replace(" ", np.nan)
data['TotalCharges'] = data['TotalCharges'].astype(float)
median_totalcharges = data['TotalCharges'].median()
data['TotalCharges'] = data['TotalCharges'].fillna(median_totalcharges)

# Convert boolean columns to integers
bool_cols = data.select_dtypes(include=['bool']).columns
for col in bool_cols:
    data[col] = data[col].astype(int)

# Map binary categorical columns 'Yes'/'No' to 1/0
binary_cols = ['gender', 'Partner', 'Dependents', 'PhoneService', 'PaperlessBilling', 'Churn']
for col in binary_cols:
    data[col] = data[col].map({'Yes': 1, 'No': 0, 'Male': 1, 'Female': 0})

# Ensure 'SeniorCitizen' is integer numeric 0/1
data['SeniorCitizen'] = data['SeniorCitizen'].astype(int)

# One-hot encode multi-category columns dropping first category
multi_cat_cols = ['MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
                  'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
                  'Contract', 'PaymentMethod']
data = pd.get_dummies(data, columns=multi_cat_cols, drop_first=True)

# Verify that 'Churn' column is numeric and has no missing values
if 'Churn' not in data.columns:
    raise ValueError("Target column 'Churn' is missing from the dataset.")
if data['Churn'].isnull().any():
    raise ValueError("Target column 'Churn' contains missing values.")
if not np.issubdtype(data['Churn'].dtype, np.number):
    data['Churn'] = data['Churn'].astype(int)

# Convert any remaining boolean columns to integers
bool_cols = data.select_dtypes(include=['bool']).columns
for col in bool_cols:
    data[col] = data[col].astype(int)

# Confirm no NULL values exist in dataset after processing
if data.isnull().any().any():
    raise ValueError("Data contains missing values after processing.")

# Save processed dataframe to new CSV file
data.to_csv(dataDir / 'ibmchurn_processed.csv', index=False)