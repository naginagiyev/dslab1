Section 1: Imports
Import pandas and numpy. Import the dataDir variable from the paths module. Do not use hardcoded file paths—construct all paths using dataDir and os.path for cross-platform compatibility.

Section 2: Load Data
Load the raw CSV file from the dataDir folder using the provided dataset filename.

Section 3: Transformations
- Drop Columns: Drop the 'customerID' column as it is an identifier with 100% uniqueness and no predictive value.

- Boolean Conversion: For the following columns with boolean-like values, map 'Yes'/'No' to 1/0 and convert to integer:
  - Partner
  - Dependents
  - PhoneService
  - PaperlessBilling
  - Churn (target column)
- For 'SeniorCitizen', ensure the dtype is integer (should already be int64, but confirm).

- TotalCharges Numeric Conversion: Convert 'TotalCharges' from string to float. Treat any empty strings (identified as blanks in EDA) as NaN and convert to 0, since those correspond to zero tenure (new customers with no charges), matching EDA findings. After conversion, ensure the column is float dtype.

- Encode Categorical Variables:
  - Columns to encode: gender, MultipleLines, InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies, Contract, PaymentMethod. Apply one-hot encoding to these columns, dropping the first category in each case to avoid multicollinearity.

- Numeric Columns: Ensure 'tenure', 'MonthlyCharges', and the now-numeric 'TotalCharges' have proper numeric types. No scaling is required, as the EDA indicates no strong outliers or severe skewness and the model selection in the next phase supports raw numeric input.

- Class Imbalance: The target 'Churn' shows moderate imbalance (minority class ~26.5%). For explainability, do not over- or under-sample at this stage; address imbalance, if needed, within the model pipeline.

Section 4: Save
Save the processed DataFrame as a CSV into a 'processed' subfolder inside dataDir, using the same filename as the input. Do not hardcode the output path—construct it using dataDir and os.path.join. Ensure that all column transformations and orderings are retained. Adhere strictly to the variable and path usage rules described below.

Path Usage Rules:
- Import path variables from the paths module: import dataDir
- Load raw data from dataDir using the provided filename
- Save processed data into a 'processed' subfolder inside dataDir, using the same filename
- Never hardcode file paths as string literals

Code Style Rules:
- All variable and function names must use camelCase (no underscores)
- No comments in the code