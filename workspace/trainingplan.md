Imports — Use pandas for data loading and manipulation, and import LogisticRegression from sklearn.linear_model. Use joblib for model saving. No other libraries are needed.

Load Processed Data — Load the processed data using dataDir / "ibmchurn_processed.csv". Do not use os or manual string paths; use only the provided variables and the / operator for construction. The filename is the original stem plus _processed before the extension.

Feature and Target Separation — Set the target as the 'Churn' column, and use all other columns as features.

Model Setup — Instantiate a LogisticRegression model from sklearn.linear_model. Set solver to 'lbfgs' and max_iter to 1000 to ensure convergence. Set class_weight to 'balanced' to address the moderate class imbalance in the target column as shown in the EDA.

Fit — Fit the logistic regression model on the training data (features and target as extracted above).

Save — Save the fitted model to workspaceDir under the filename "model.pkl" using joblib. Model should not be saved in any subdirectory, and no file path should be hardcoded. Use only the workspaceDir variable and / operator for path construction.

Path Usage Rules —
- Do not import path variables in the generated code. The variables dataDir and workspaceDir are already available in the execution context—importing them again will cause duplicate imports and errors.
- Do not import os. Use the / operator on Path objects for all path construction (e.g. dataDir / "file.csv").
- Processed data is loaded from dataDir using the processed filename as described.
- The fitted model is saved into workspaceDir under the filename model.pkl, using joblib.
- No file path should ever be hardcoded as a string literal.

Code Style Rules —
- All variable and function names that the code defines must use camelCase. No underscores in user-defined names.
- Add a short, informative comment at the start of each section (e.g. # load processed data, # define model). No inline comments.

