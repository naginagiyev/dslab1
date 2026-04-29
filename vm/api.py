from typing import Any, List
from fastapi import FastAPI
from pydantic import create_model
from prediction import predict, featureNames

app = FastAPI()
fields = {name: (Any, ...) for name in featureNames}
DynamicInput = create_model("DynamicInput", **fields)

@app.get("/")
def root():
    return {"status": "API is running"}

@app.post("/predict")
def predictEndpoint(inputData: List[DynamicInput]):
    input_dicts = [item.model_dump() for item in inputData]
    result = predict(input_dicts)
    return {"prediction": result}