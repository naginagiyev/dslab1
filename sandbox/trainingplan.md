Imports — Use pandas for reading the processed csv, sklearn.linear_model for LogisticRegression, and joblib for model serialization. Do not import any path objects ('dataDir', 'workspaceDir') or os. All path operations must use the / operator on provided Path variables.

Load Processed Data — Load the processed data using pandas.read_csv with the path dataDir / 'ibmchurn_processed.csv'.

Feature and Target Separation — Separate the features (all columns except 'Churn') from the target column ('Churn'). Assign the features dataframe to 'X' and the target series to 'y'.

Model Setup — Instantiate a LogisticRegression model from sklearn.linear_model. Set class_weight='balanced' to account for the moderate target imbalance. Use solver='liblinear' for robustness with binary datasets. Leave other hyperparameters as default.

Fit — Fit the logistic regression model on the feature matrix 'X' and target 'y'.

Save — Save the trained logistic regression model using joblib.dump into workspaceDir / 'model.pkl'. Do not hardcode file paths; follow the variable naming and path rules strictly.