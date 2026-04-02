import os
import json
from pydantic import BaseModel
from path import promptsDir, configDir
from models.generation import GenerationModel

class ConsultationReport(BaseModel):
    taskType: str | None
    targetCol: str | None
    desiredMetric: str | None
    minScoreRequirement: float | None
    explainableModel: bool
    saveModel: bool
    writeReport: bool
    deployment: bool

class Consultant:
    def __init__(self):
        self.history = []
        self.questionAgent = GenerationModel(os.path.join(promptsDir, "consultant.md"))
        self.reportAgent = GenerationModel(
            os.path.join(promptsDir, "consultantassistant.md"),
            responseFormat=ConsultationReport
        )

    def nextQuestion(self, userInput: str):
        response = self.questionAgent.generate(query=userInput, history=self.history)
        if response.strip() == "[OFFTOPIC]":
            prev = next((h["assistant"] for h in reversed(self.history) if h["assistant"].strip() not in ("[DONE]", "[OFFTOPIC]")), "Should the model be explainable?")
            return f"I think the query you have written is not related to our topic. So, I am asking again {prev}"
        self.history.append({"user": userInput, "assistant": response})
        if response.strip() == "[DONE]":
            return None
        return response

    def saveReport(self):
        conversation = "\n".join(
            f"User: {h['user']}\nAssistant: {h['assistant']}"
            for h in self.history
        )
        report = self.reportAgent.generate(query=conversation)
        os.makedirs(configDir, exist_ok=True)
        with open(os.path.join(configDir, "consultation.json"), "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=4)
        return report