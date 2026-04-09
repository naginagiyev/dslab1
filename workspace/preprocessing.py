# initialize paths
from paths import workspaceDir, dataDir

# Generated code starts here
# import necessary libraries
import pandas as pd
import numpy as np

# load raw data
dataPath = dataDir / "ibmchurn.csv"
rawData = pd.read_csv(dataPath)

# drop identifier column
rawData.drop(columns=['customerID'], inplace=True)

# fix TotalCharges type
rawData['TotalCharges'] = pd.to_numeric(rawData['TotalCharges'], errors='coerce')
rawData['TotalCharges'].fillna(0.0, inplace=True)

# encode boolean columns
boolColumns = ['Partner', 'Dependents', 'PhoneService', 'PaperlessBilling', 'Churn']
for col in boolColumns:
    rawData[col] = rawData[col].map({'Yes': 1, 'No': 0})

# encode categorical columns with one-hot encoding
categoricalColumns = ['gender', 'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup', 
                      'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract', 'PaymentMethod']
rawData = pd.get_dummies(rawData, columns=categoricalColumns, drop_first=True)

# ensure numeric columns are present as numeric types
numericColumns = ['tenure', 'MonthlyCharges', 'TotalCharges']
for col in numericColumns:
    rawData[col] = pd.to_numeric(rawData[col])

# final cleanup: verify no object-typed columns remain
objectCols = rawData.select_dtypes(include='object').columns
if len(objectCols) > 0:
    rawData[objectCols] = rawData[objectCols].apply(lambda x: x.astype('category').cat.codes)

# save the processed dataframe
processedPath = dataDir / "ibmchurn_processed.csv"
rawData.to_csv(processedPath, index=False)