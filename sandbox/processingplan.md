Imports — Use pandas for DataFrame manipulation and numpy for array operations. No other libraries are needed for the required transformations.

Load Data — Load the raw CSV directly from dataDir using the provided dataset filename 'ibmchurn.csv'. Do not use os or any string-based path operations; rely on the / operator for joining Path objects.

Transformations
1. Drop Columns — Remove the column 'customerID' entirely, as EDA identifies it as an identifier column and not a useful feature.
2. Convert Data Types
    - Convert 'TotalCharges' from string/object dtype to numeric (float). Coerce errors to NaN and treat any resulting NaNs as missing. According to the EDA, only 11 rows contain an empty string in 'TotalCharges'; proceed to impute these.
3. Handle Missing Values
    - For the 11 missing values in 'TotalCharges', impute with the median value of 'TotalCharges' (computed after conversion to numeric). No other missing values are present in the dataset.
4. Encode Boolean Columns
    - For columns with boolean-like values ('Yes'/'No'): 'Partner', 'Dependents', 'PhoneService', 'PaperlessBilling', and the target column 'Churn' — map 'Yes' to 1 and 'No' to 0.
    - For 'SeniorCitizen', which is already {0,1}, leave as is.
5. Encode Categorical Columns
    - For all categorical columns with more than two categories, apply one-hot encoding using pandas get_dummies with drop_first=True to prevent collinearity. This applies to: 'gender', 'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract', and 'PaymentMethod'.
    - For binary categoricals such as 'gender', use one-hot encoding with drop_first=True. For multiclass categoricals, this will result in n-1 dummy variables for each.
6. Scale Numeric Columns
    - For 'tenure' (numeric_discrete) and 'MonthlyCharges' and 'TotalCharges' (both numeric_continuous), scale these columns using standardization (subtract mean and divide by standard deviation). No outlier treatment is needed per the EDA.

Save — Save the fully processed DataFrame into dataDir, using the original filename stem and appending '_processed' before the extension (ibmchurn_processed.csv). Do not write to any subdirectory.

Path Usage Rules for the code-writing agent:
- Do not import dataDir or sandboxDir; they are already available.
- Do not import os. Build all paths using the / operator on Path objects.
- Load raw data from dataDir using the original filename.
- Save processed data to dataDir, appending '_processed' to the original filename before the extension.

Code Style Rules for the code-writing agent:
- Variable and function names must use camelCase with no underscores in user-defined names.
- Begin each code section with a short, informative comment describing its purpose (e.g., 'load raw data', 'encode categoricals'). No inline comments.