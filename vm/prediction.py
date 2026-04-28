import os
import json
import joblib
import pandas as pd
import onnxruntime as rt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
preprocessor = joblib.load(os.path.join(BASE_DIR, "preprocessor.pkl"))
session = rt.InferenceSession(os.path.join(BASE_DIR, "model.onnx"))
inputName = session.get_inputs()[0].name

with open(os.path.join(BASE_DIR, "configuration.json"), "r", encoding="utf-8") as f:
    configuration = json.load(f)

featureNames = configuration.get("columnNames")
taskType = configuration.get("taskType")

def predict(inputData):
    df = pd.DataFrame(inputData)
    df = df[featureNames]
    transformed = preprocessor.transform(df).astype("float32")
    if taskType == "time-series":
        transformed = transformed.reshape(1, transformed.shape[0], transformed.shape[1])
    result = session.run(None, {inputName: transformed})
    return result[0].tolist()