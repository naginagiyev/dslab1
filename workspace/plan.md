# ML Project Plan

## Project Overview
This project is a binary classification task to predict customer churn using the dataset at `data\ibmchurn.csv`. The target column is `Churn`. Based on the moderate class imbalance, tabular feature types, and requirement for explainability, the primary model will be `sklearn.ensemble.RandomForestClassifier`. The key evaluation metric is the F1 score, and the project requires a minimum test F1 score threshold of 0.8. The pipeline will include explainability using SHAP, model saving, but will not require report generation or deployment.

## Phase 1 — Preprocessing

1. **Drop Identifier Columns**: Remove the `customerID` column as it is an ID-like field and not predictive.
2. **Convert Boolean Values**: For columns with ["No", "Yes"] or [0, 1] semantics (`SeniorCitizen`, `Partner`, `Dependents`, `PhoneService`, `PaperlessBilling`, `Churn`), convert values to binary integers (0 and 1) for modeling.
3. **Convert 'TotalCharges' to Numeric**: Coerce the `TotalCharges` column to `float` type. Strip whitespace, set errors='coerce' (invalid parses to NaN). Since there are only 11 rows with blank `TotalCharges`, drop these rows.
4. **Encode Binary Categorical Values**: For `gender`, encode as binary (e.g., Male=1, Female=0).
5. **One-Hot Encode Multi-category Categorical Columns**: Apply `sklearn.preprocessing.OneHotEncoder` (with drop='first', sparse=False) to columns with >2 unique values and inferred type categorical: `MultipleLines`, `InternetService`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`, `Contract`, `PaymentMethod`.
6. **Scale Numeric Features**: Apply `sklearn.preprocessing.StandardScaler` to `tenure`, `MonthlyCharges`, and `TotalCharges`.
7. **Address Class Imbalance**: Use `imblearn.over_sampling.SMOTE` with default parameters to balance the minority class in the training set.
8. **Train/Test Split**: Split data into train and test sets with `sklearn.model_selection.train_test_split`, setting test size to 20%, stratifying by the `Churn` target column, and setting random_state=42.

## Phase 2 — Feature Engineering
No custom feature engineering required.

## Phase 3 — Feature Selection
Use `sklearn.feature_selection.SelectFromModel` with estimator set to `RandomForestClassifier(n_estimators=100, random_state=42)`. Set the importance threshold to 'median' (i.e., keep features with impurity-based importance above the median).

## Phase 4 — Model Training

1. Train a `sklearn.ensemble.RandomForestClassifier` with `n_estimators=200`, `class_weight='balanced'`, and `random_state=42`. This model is chosen for its tabular performance and compatibility with SHAP.
2. Fit the model on the selected features of the resampled training set.
3. Use `sklearn.model_selection.cross_val_score` with 5-fold cross-validation, scoring by 'f1', and log fold scores and the mean value.

## Phase 5 — Evaluation
- Predict on the test set and compute the F1 score using `sklearn.metrics.f1_score`.
- If the test F1 score is below 0.8, abort and log a failure message.

## Phase 6 — Hyperparameter Tuning

- Use `sklearn.model_selection.GridSearchCV` with the following parameter grid:
    - `n_estimators`: [100, 200, 300]
    - `max_depth`: [5, 10, 20, None]
    - `min_samples_split`: [2, 5, 10]
    - `class_weight`: ['balanced']
    - `random_state`: [42]
- Set `cv=5`, `scoring='f1'`, `n_jobs=-1`, and `refit=True`.
- Fit the grid search on the training set after feature selection and SMOTE.
- After identifying the best estimator, refit it on the full training data and re-evaluate on the test set, logging the best parameters and final F1 score.

## Phase 7 — Explainability

- Use `shap.TreeExplainer` with the final trained `RandomForestClassifier`.
- Compute SHAP values on the training set after preprocessing and feature selection.
- Calculate mean absolute SHAP values for each (input) feature.
- Log the mean absolute SHAP values as a printed, descending-sorted table showing feature name and value.

## Phase 8 — Model Saving

- Save the best model, along with the fitted scaler, encoder, and feature selection objects, using `joblib.dump`.
- Use the filename convention: `rf_churn_best_model.joblib`.