Imports — Use pandas for data manipulation and numpy for numeric operations. No need to import path management libraries (`dataDir`, `workspaceDir`) as they are already available. Do not import os. Do not import encoding utilities such as LabelEncoder or OneHotEncoder; use pd.get_dummies for one-hot encoding where required.

Load Data — Load the raw data from dataDir using the filename 'ibmchurn.csv'. Read the CSV directly using dataDir / 'ibmchurn.csv', without path construction or os.path.join.

Transformations — Perform the following steps in order:
1. Drop the column 'customerID' as it is an id-like column that does not provide predictive value.
2. Convert the 'TotalCharges' column from string/object to numeric type. Coerce errors (such as possible empty string values) into NaN. Then, fill any resulting NaN values with 0, as the small number of missing or empty entries likely correspond to customers with zero tenure and zero charges.
3. Convert all boolean columns with values 'Yes'/'No' to 1/0 integer format. These columns are: 'Partner', 'Dependents', 'PhoneService', 'PaperlessBilling', and 'Churn'. Map 'Yes' to 1 and 'No' to 0 for each of these columns.
4. Ensure 'SeniorCitizen' remains as integer type where 1 is True and 0 is False. No change needed unless loaded dtype is object.
5. One-hot encode the following categorical columns using pd.get_dummies with drop_first=True to avoid multicollinearity: 'gender', 'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract', 'PaymentMethod'. Apply get_dummies to these columns. Do not one-hot encode the boolean or numeric columns.
6. Confirm that 'tenure' and 'MonthlyCharges' are numerics. No scaling or outlier processing is needed, as EDA shows no significant outliers and only minor skew.
7. Review the final DataFrame to ensure all features are numeric and there are no remaining object dtypes (besides the target, if any). The target ('Churn') should already be mapped to 0/1 as previously handled.

Save — Save the fully processed DataFrame to dataDir using the filename 'ibmchurn_processed.csv' (i.e., append '_processed' before the extension). Do not create any subdirectories. Use the / operator on Path objects for all path handling. Do not hardcode file paths as string literals.

Path Usage Rules — Do not import dataDir or workspaceDir, and do not import os. Use the / operator on the existing dataDir Path object to refer to and save files. Only modify filename stems as described for processed output. Do not create subdirectories.

Code Style Rules — All variable and function names must be in camelCase with no underscores. Add a short, informative comment at the start of each section. No inline comments should be used.