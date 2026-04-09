Imports — Use pandas for data manipulation and numpy for numerical operations. No other libraries are needed for the specified transformations.

Load Data — Load the raw data CSV using dataDir / "ibmchurn.csv". Do not use os or manual path concatenation; the dataDir variable is already available in the environment.

Transformations —
# Drop identifier column: Remove the 'customerID' column entirely, as it serves as a unique identifier and does not provide predictive value.
# Fix 'TotalCharges' type: Convert the 'TotalCharges' column from object to numeric, coercing any errors (such as blank spaces) to NaN, then fill any resulting NaN values with 0.0 (these correspond to customers with tenure 0, i.e., new customers who have not yet been billed).
# Encode boolean columns: For columns with two values, ['Yes', 'No'], map them to 1 and 0 respectively. Apply this to 'Partner', 'Dependents', 'PhoneService', 'PaperlessBilling', and 'Churn'. For 'SeniorCitizen', ensure it's an integer column with 0/1 (it is already int64, so no change needed).
# Encode categorical columns: For all other categorical columns, use one-hot encoding with pandas get_dummies. Apply this to: 'gender', 'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract', and 'PaymentMethod'. Drop the first category for each column to avoid multicollinearity.
# Numeric columns: Ensure 'tenure', 'MonthlyCharges', and the newly converted 'TotalCharges' are present as numeric columns and have no further transformation, as there are no missing values or outliers per EDA.
# Final cleanup: Verify there are no remaining object-typed columns.

Save — Save the processed DataFrame directly to dataDir with the name "ibmchurn_processed.csv". Do not create any subfolders and do not hardcode file paths.

Path Usage Rules —
- Do not import path variables in the generated code. The variables dataDir and workspaceDir are already available in the execution context—importing them again will cause duplicate imports and errors.
- Do not import os. Use the / operator on Path objects for all path construction (e.g. dataDir / "file.csv").
- Raw data is loaded from dataDir using the dataset filename given in the inputs.
- Processed data is saved directly into dataDir using the original filename with _processed appended before the extension (e.g. ibmchurn.csv → ibmchurn_processed.csv). Do not create any subdirectory.
- No file path should ever be hardcoded as a string literal.

Code Style Rules —
- All variable and function names that the code defines must use camelCase. No underscores in user-defined names.
- Add a short, informative comment at the start of each section (e.g. # load raw data, # encode categoricals). No inline comments.

