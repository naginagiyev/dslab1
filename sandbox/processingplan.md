Imports — Use pandas for dataframe operations and numpy for numerical type conversions. Do not import any path objects ('dataDir', 'workspaceDir') or os. All path operations must use the / operator on provided Path variables. Do not use label encoders or one-hot encoders from sklearn; use pandas get_dummies for any one-hot encoding.

Load Data — Load the raw data using pandas.read_csv with the file path constructed as dataDir / 'ibmchurn.csv'.

Transformations —
1. Drop the 'customerID' column, as it is identified as an ID-like column with no predictive value.
2. Clean and convert the 'TotalCharges' column:
   - Replace any blank strings (" ") in 'TotalCharges' with numpy.nan, then convert the column to float type.
   - For any still-missing values after this conversion, as they are very few (0.16%), impute using the median of the column.
3. Encode binary categorical/boolean columns ('gender', 'Partner', 'Dependents', 'PhoneService', 'PaperlessBilling', 'Churn') by mapping 'Yes' to 1 and 'No' to 0.
4. Ensure 'SeniorCitizen' is a numeric column with values 0/1; coerce to integer type if necessary.
5. For all other categorical columns with >2 categories ('MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract', 'PaymentMethod'), convert to one-hot encoded (dummy) columns using pandas get_dummies, dropping the first category for each to avoid collinearity (drop_first=True).
6. No missing value imputation is needed beyond 'TotalCharges', as all other columns contain 0% missing.
7. Outlier handling is not necessary as EDA found zero outliers in all numeric columns.
8. No normalization or scaling is needed, as the selected model (Logistic Regression for explainability) can handle unscaled features for this mix of numeric and dummy variables, but ensure all columns are either numeric or dummy (no object types remain except the column headers).

Save — Save the processed dataframe using pandas.to_csv into dataDir, with the filename 'ibmchurn_processed.csv' (inserting '_processed' before the extension), with index=False. Do not save to a subdirectory.