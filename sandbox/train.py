# initialize paths
from paths import dataDir
from paths import workspaceDir

# Generated code starts here
# Imports
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib

# Load Processed Data
df = pd.read_csv(dataDir / 'ibmchurn_processed.csv')

# Feature and Target Separation
X = df.drop(columns='Churn')
y = df['Churn']

# Model Setup
model = LogisticRegression(class_weight='balanced', solver='liblinear', max_iter=100)

# Fit the Model
model.fit(X, y)

# Predict on training data
y_pred = model.predict(X)

# Calculate accuracy
accuracy = accuracy_score(y, y_pred)

# Print training results
print(f"Training complete. Accuracy on training set: {accuracy:.4f}")

# Save the Trained Model
joblib.dump(model, workspaceDir / 'model.pkl')