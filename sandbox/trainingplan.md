Imports — Use pandas for loading the processed dataset. Import scikit-learn's LogisticRegression for modeling, since explainability is requested and Logistic Regression is the most explainable model choice per Model Options. Import joblib for saving the fitted model. Do not import dataDir or sandboxDir, do not import os.

Load Processed Data — Load the processed CSV from dataDir using the filename with '_processed' appended before the extension ('ibmchurn_processed.csv'). Path construction must use the / operator on Path objects, never strings or os.

Feature and Target Separation — Identify the target column 'Churn' for modeling. Separate the features (all columns except 'Churn') and the target variable (the 'Churn' column). Assign these to variables named X and y, respectively.

Model Setup — Instantiate a LogisticRegression model. Optionally, if dataset is large or many features result from encoding, set 'max_iter' to a higher value such as 1000 for convergence. Do not set other hyperparameters unless justified by EDA (none needed here). Since class imbalance is moderate, set class_weight='balanced' to help the model learn both classes effectively.

Fit — Fit the LogisticRegression model on X and y using the model's fit method.

Save — Save the fitted model object to sandboxDir as 'model.pkl' using joblib. Path construction must use / on Path objects with no hardcoded strings.

Path Usage Rules for the code-writing agent:
- Do not import dataDir or sandboxDir; they are already available.
- Do not import os. Build all paths using the / operator on Path objects.
- Load processed data from dataDir using the '_processed' filename.
- Save model to sandboxDir under the filename 'model.pkl'.

Code Style Rules for the code-writing agent:
- Variable and function names must use camelCase with no underscores in user-defined names.
- Begin each code section with a short, informative comment describing its purpose (e.g., 'load processed data', 'fit logistic regression'). No inline comments.