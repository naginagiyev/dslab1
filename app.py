import sys
sys.dont_write_bytecode = True

import json
import logging
import pandas as pd
from pathlib import Path
from tools.eda import EDA
from agents.planner import Planner
from agents.consultant import Consultant
from agents.configfiller import ConfigFiller
from agents.processoragent import ProcessorAgent
from paths import configDir, workspaceDir

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

log = logging.getLogger(__name__)


def runEDA(datasetPath: str, targetCol: str, taskType: str):
    if not targetCol or not taskType:
        log.warning(f"EDA skipped — targetCol={targetCol}, taskType={taskType}")
        return
    log.info(f"Running EDA — target: {targetCol}, task: {taskType}")
    workspaceDir.mkdir(parents=True, exist_ok=True)
    eda = EDA(inputPath=datasetPath, targetCol=targetCol, taskType=taskType)
    stem = Path(datasetPath).stem
    eda.outputPath = str(workspaceDir / f"{stem}eda.md")
    eda.run()
    log.info(f"EDA complete — report saved to {eda.outputPath}")


def inferTaskTypeFromTarget(datasetPath: str, targetCol: str) -> str:
    df = pd.read_csv(datasetPath)
    target = df[targetCol].dropna()
    uniqueCount = int(target.nunique(dropna=True))
    totalCount = int(len(target))
    uniqueRatio = (uniqueCount / totalCount) if totalCount else 0.0
    numericTarget = pd.to_numeric(target, errors="coerce")
    numericRatio = float(numericTarget.notna().mean()) if totalCount else 0.0

    if uniqueCount == 2:
        return "binary-classification"
    if numericRatio > 0.95 and uniqueCount > 20 and uniqueRatio > 0.05:
        return "regression"
    return "multi-class-classification"


def main():
    print("=== Agentic Machine Learning Automation ===\n")

    while True:
        datasetPath = input("Path to your dataset: ").strip()
        if not datasetPath:
            print("Cancelled.")
            return
        if not Path(datasetPath).exists():
            print("File not found. Try again.\n")
            continue
        break

    log.info(f"Dataset accepted: {datasetPath}")

    print("\nShould I ask you questions about the project?")
    print("  A. Sure, go ahead")
    print("  B. No, leave it all to you")
    consent = input("Choice (A/B): ").strip().upper()

    if consent == "B":
        log.info("Auto mode — skipping consultation save and detecting target automatically")
        consultant = Consultant()
        log.info("Consultant — detecting target column")
        detectedTarget = consultant.detectTarget(datasetPath, report=None, save=False)
        inferredTaskType = inferTaskTypeFromTarget(datasetPath, detectedTarget)
        log.info(
            "Auto mode — inferred task type for EDA: %s (target=%s)",
            inferredTaskType,
            detectedTarget,
        )

        runEDA(datasetPath, detectedTarget, inferredTaskType)

        filler = ConfigFiller()
        log.info("ConfigFiller — filling full configuration from EDA without consultation JSON")
        filler.fill(
            datasetPath,
            consultation=None,
            targetCol=detectedTarget,
            includeConsultation=False,
            save=True,
        )
        log.info("Configuration saved to configuration/consultation.json")

        log.info("Planner — creating project plan")
        planner = Planner()
        preprocessingPath, trainingPath = planner.createPlan(datasetPath)
        log.info(f"Processing plan saved to {preprocessingPath}")
        log.info(f"Training plan saved to {trainingPath}")
        log.info("ProcessorAgent — running preprocessing")
        ProcessorAgent().preprocess()
        print("\nDone.")
        return

    log.info("Interactive mode — starting consultation")
    consultant = Consultant()
    userInput = f"Dataset Path: {datasetPath}"

    while True:
        log.info("Consultant — generating next question")
        question = consultant.nextQuestion(userInput)
        if question is None:
            log.info("Consultant — no more questions")
            break
        print(f"\nBot: {question}")
        userInput = input("You: ").strip()
        if not userInput:
            print("Cancelled.")
            return

    log.info("Consultant — saving report")
    report = consultant.saveReport()
    log.info("Consultant — detecting target column")
    consultant.detectTarget(datasetPath, report)
    log.info("Consultation saved to configuration/consultation.json")

    with open(configDir / "consultation.json", "r", encoding="utf-8") as f:
        consultation = json.load(f)
    targetCol = consultation.get("targetCol")
    taskType = consultation.get("taskType")
    runEDA(datasetPath, targetCol, taskType)

    filler = ConfigFiller()
    log.info("ConfigFiller — filling remaining null fields using EDA report")
    filler.fill(datasetPath)

    log.info("Planner — creating project plan")
    planner = Planner()
    preprocessingPath, trainingPath = planner.createPlan(datasetPath)
    log.info(f"Processing plan saved to {preprocessingPath}")
    log.info(f"Training plan saved to {trainingPath}")
    log.info("ProcessorAgent — running preprocessing")
    ProcessorAgent().preprocess()
    print("\nDone.")


if __name__ == "__main__":
    main()
