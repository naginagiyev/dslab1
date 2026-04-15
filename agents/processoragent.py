import os
import json
import pandas as pd
from llms.codex import CodexModel
from tools.coderunner import CodeRunner
from paths import workspaceDir, configDir, dataDir, promptsDir

class ProcessorAgent:
    def __init__(self):
        self.coder = CodexModel()
        self.runner = CodeRunner(fileName="processing.py")
        self.lastReasoning = None
        self.lastGeneratedCode = None
        self.consultationPath = configDir / "consultation.json"
        planPath = workspaceDir / "processingplan.md"

        with open(planPath, 'r', encoding="utf-8") as plan:
            self.plan = plan.read()
        with open(self.consultationPath, 'r', encoding="utf-8") as consultationFile:
            self.consultation = json.load(consultationFile)
        with open(promptsDir / "processorreasoningprompt.md", "r", encoding="utf-8") as f:
            self.reasoningPrompt = f.read()

    def preprocess(self):
        output = self.act()
        while True:
            reasoning = self.reason(output=output)
            if reasoning.condition == "pass":
                break
            output = self.fixCode()

    def act(self) -> str:
        header = f"Dataset Path: {self.consultation['dataFile']}\n\n"
        generatedCode = self.coder.code(header + self.plan)
        self.lastGeneratedCode = generatedCode
        self.runner.add(generatedCode)
        return self.runner.getOutput()

    def fixCode(self) -> str:
        fixedCode = self.coder.fixCode(self.lastGeneratedCode, self.lastReasoning)
        self.lastGeneratedCode = fixedCode
        self.runner.add(fixedCode)
        return self.runner.getOutput()

    def reason(self, output: str) -> dict:
        if output["operation"] == "success":
            generatedReasoning = self.coder.reason(self.reasoningPrompt, json.dumps(self.getDataInfo(), indent=2))
        else:
            generatedReasoning = self.coder.reason(self.reasoningPrompt, output["output"])
        self.lastReasoning = generatedReasoning.prompt
        return generatedReasoning

    def getDataInfo(self) -> dict:
        dataFile = self.consultation['dataFile']
        base, ext = os.path.splitext(os.path.basename(dataFile))
        processedBasename = f"{base}_processed{ext}"
        processedDataPath = dataDir / processedBasename
        processedData = pd.read_csv(processedDataPath)

        self.consultation['processedDataFile'] = processedBasename
        with open(self.consultationPath, 'w', encoding="utf-8") as consultationFile:
            json.dump(self.consultation, consultationFile, indent=2)

        runtimeConfigPath = configDir / "runtimeconfig.json"
        with open(runtimeConfigPath, 'r', encoding="utf-8") as f:
            runtimeConfig = json.load(f)
        runtimeConfig['processedDataFile'] = processedBasename
        with open(runtimeConfigPath, 'w', encoding="utf-8") as f:
            json.dump(runtimeConfig, f, indent=2)

        return {
            col: {
                "non_null_count": int(processedData[col].notnull().sum()),
                "dtype": str(processedData[col].dtype)
            }
            for col in processedData.columns
        }