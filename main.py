import sys

# do not let the pycaches to appear
sys.dont_write_bytecode = True

import json
import logging
import runpy
import shutil
import click
import pandas as pd
import questionary
from pathlib import Path
from tools.eda import EDA
from rich.text import Text
from rich.panel import Panel
from questionary import Style
from rich.console import Console
from agents.planner import Planner
from agents.consultant import Consultant
from agents.configfiller import ConfigFiller
from agents.processoragent import ProcessorAgent
from agents.trainagent import TrainAgent
from agents.evaluationagent import EvaluationAgent
from agents.reporter import ReportWriter
from tools.datasplitter import split as splitData
from paths import configDir, sandboxDir, toolsDir, modelsDir, vmDir

custom_style = Style([
    ('selected', 'fg:#ff8c00 bold'),
    ('pointer', 'fg:#ff8c00 bold'),
    ('highlighted', 'fg:#ff8c00 bold'),
])

console = Console()

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

def ensureConfiguration():
    configDir.mkdir(parents=True, exist_ok=True)
    configurationPath = configDir / "configuration.json"
    if not configurationPath.exists():
        with open(configurationPath, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)

def runEDA(datasetPath: str, targetCol: str, taskType: str):
    if not targetCol or not taskType:
        return
    sandboxDir.mkdir(parents=True, exist_ok=True)
    eda = EDA(inputPath=datasetPath, targetCol=targetCol, taskType=taskType)
    stem = Path(datasetPath).stem
    eda.outputPath = str(sandboxDir / f"{stem}eda.md")
    eda.run()

def copyArtifactsToVm():
    vmDir.mkdir(parents=True, exist_ok=True)
    for item in modelsDir.iterdir():
        shutil.copy2(item, vmDir / item.name) if item.is_file() else shutil.copytree(item, vmDir / item.name, dirs_exist_ok=True)
    configSrc = configDir / "configuration.json"
    if configSrc.exists():
        shutil.copy2(configSrc, vmDir / "configuration.json")

def checkAndWriteReport():
    with open(configDir / "configuration.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    if config.get("writeReport") is True:
        ReportWriter().writeReport()


def checkAndDeploy():
    with open(configDir / "configuration.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    if config.get("deployment") is True:
        copyArtifactsToVm()
        runpy.run_path(str(toolsDir / "transfer.py"), run_name="__main__")
        runpy.run_path(str(toolsDir / "deployer.py"), run_name="__main__")

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

def printBotResponse(response: str):
    console.print(f"\n[bold cyan]  🤖 Bot:[/bold cyan] {response}")

@click.command()
def main():
    ensureConfiguration()
    text = Text()
    text.append("🤖  Agentic Machine Learning Automation", style="bold cyan")
    console.print(Panel(text, border_style="cyan", padding=(1, 4)))
    console.print()

    while True:
        datasetPath = questionary.path("📂  Path to your dataset:", only_directories=False).ask()

        if datasetPath is None:
            console.print("[yellow]  ⚠️  Cancelled.[/yellow]")
            return

        if not Path(datasetPath).exists():
            console.print("[red]  ❌  I don't see a dataset at that path. Are you sure you entered it right?[/red]\n")
            continue
        break

    console.print(f"[green]  ✅  Dataset exists in[/green] [dim]{datasetPath}[/dim]\n")

    console.print()
    consent = questionary.select(
        "Is it okay that I asked you about project?",
        choices=["A. Sure. Go ahead!", "B. No, I leave it all to you!"],
        style=custom_style
    ).ask()

    if consent is None:
        console.print("[yellow]  ⚠️  Cancelled.[/yellow]")
        return

    if consent.startswith("B."):
        consultant = Consultant()
        detectedTarget = consultant.detectTarget(datasetPath, report=None, save=False)
        inferredTaskType = inferTaskTypeFromTarget(datasetPath, detectedTarget)

        runEDA(datasetPath, detectedTarget, inferredTaskType)

        filler = ConfigFiller()
        filler.fill(
            datasetPath,
            consultation=None,
            targetCol=detectedTarget,
            includeConsultation=False,
            save=True,
        )
        console.print()
        console.print(
            Panel(
                "[bold green]✅  Understood! Proceeding automatically...[/bold green]\n[dim]Configuration generated from EDA and saved to ./configuration/configuration.json[/dim]",
                border_style="green", padding=(1, 4))
        )
        console.print()
        console.print("[bold magenta]  📋  Generating processing plan...[/bold magenta]")
        planner = Planner()
        preprocessingPath = planner.createPreProcessingPlan()
        console.print()
        console.print(
            Panel(
                f"[bold green]✅  Processing plan created![/bold green]\n[dim]Processing plan saved to {preprocessingPath}[/dim]",
                border_style="green", padding=(1, 4))
        )
        console.print()
        console.print("[bold magenta]  ⚙️  Running preprocessing...[/bold magenta]")
        ProcessorAgent().preprocess()
        console.print()
        console.print("[bold magenta]  ✂️  Splitting data...[/bold magenta]")
        splitData()
        console.print()
        console.print("[bold magenta]  📋  Generating training plan...[/bold magenta]")
        trainingPath = planner.createTrainingPlan()
        console.print()
        console.print(
            Panel(
                f"[bold green]✅  Training plan created![/bold green]\n[dim]Training plan saved to {trainingPath}[/dim]",
                border_style="green", padding=(1, 4))
        )
        console.print()
        console.print("[bold magenta]  🧠  Training model...[/bold magenta]")
        TrainAgent().train()
        console.print()
        console.print("[bold magenta]  🎛️  Tuning model parameters...[/bold magenta]")
        EvaluationAgent().tune()
        console.print()
        console.print("[bold magenta]  🔍  Running feature decider...[/bold magenta]")
        runpy.run_path(str(toolsDir / "featuredecider.py"), run_name="__main__")
        checkAndDeploy()
        checkAndWriteReport()
        return

    console.print()
    console.print("[bold magenta]  ❓  Preparing questions...[/bold magenta]")

    consultant = Consultant()
    userInput = f"Dataset Path: {datasetPath}"

    while True:
        question = consultant.nextQuestion(userInput)

        if question is None:
            break

        printBotResponse(question)

        userInput = questionary.text("💬 You:").ask()

        if userInput is None:
            console.print("[yellow]⚠️  Cancelled.[/yellow]")
            return

    report = consultant.saveReport()
    consultant.detectTarget(datasetPath, report)
    with open(configDir / "configuration.json", "r", encoding="utf-8") as f:
        consultation = json.load(f)
    runEDA(
        datasetPath,
        consultation.get("targetCol"),
        consultation.get("taskType"),
    )
    filler = ConfigFiller()
    filler.fill(datasetPath)

    console.print()
    console.print(
        Panel(
            "[bold green]✅  Not any question! Consultation complete![/bold green]\n[dim]Configuration saved to ./configuration/configuration.json[/dim]",
            border_style="green", padding=(1, 4))
    )

    console.print()
    console.print("[bold magenta]  📋  Generating processing plan...[/bold magenta]")
    planner = Planner()
    preprocessingPath = planner.createPreProcessingPlan()
    console.print()
    console.print(
        Panel(
            f"[bold green]✅  Processing plan created![/bold green]\n[dim]Processing plan saved to {preprocessingPath}[/dim]",
            border_style="green", padding=(1, 4))
    )
    console.print()
    console.print("[bold magenta]  ⚙️  Running preprocessing...[/bold magenta]")
    ProcessorAgent().preprocess()
    console.print()
    console.print("[bold magenta]  ✂️  Splitting data...[/bold magenta]")
    splitData()
    console.print()
    console.print("[bold magenta]  📋  Generating training plan...[/bold magenta]")
    trainingPath = planner.createTrainingPlan()
    console.print()
    console.print(
        Panel(
            f"[bold green]✅  Training plan created![/bold green]\n[dim]Training plan saved to {trainingPath}[/dim]",
            border_style="green", padding=(1, 4))
    )
    console.print()
    console.print("[bold magenta]  🧠  Training model...[/bold magenta]")
    TrainAgent().train()
    console.print()
    console.print("[bold magenta]  🎛️  Tuning model parameters...[/bold magenta]")
    EvaluationAgent().tune()
    console.print()
    console.print("[bold magenta]  🔍  Running feature decider...[/bold magenta]")
    runpy.run_path(str(toolsDir / "featuredecider.py"), run_name="__main__")
    checkAndDeploy()
    checkAndWriteReport()

if __name__ == "__main__":
    main()