import sys

# do not let the pycaches to appear
sys.dont_write_bytecode = True

import json
import click
import questionary
from pathlib import Path
from rich.text import Text
from rich.panel import Panel
from questionary import Style
from rich.console import Console
from agents.planner import Planner
from path import configDir, workspaceDir, edaDir
from agents.consultant import Consultant

custom_style = Style([
    ('selected', 'fg:#ff8c00 bold'),
    ('pointer', 'fg:#ff8c00 bold'),
    ('highlighted', 'fg:#ff8c00 bold'),
])

console = Console()

def runEDA(datasetPath: str):
    sys.path.insert(0, str(edaDir))
    from eda import EDA
    with open(configDir / "consultation.json", "r") as f:
        consultation = json.load(f)
    targetCol = consultation.get("targetCol")
    taskType = consultation.get("taskType")
    if targetCol and taskType:
        workspaceDir.mkdir(parents=True, exist_ok=True)
        eda = EDA(inputPath=datasetPath, targetCol=targetCol, taskType=taskType)
        stem = Path(datasetPath).stem
        eda.outputPath = str(workspaceDir / f"{stem}eda.md")
        eda.run()
    sys.path.pop(0)

def printBotResponse(response: str):
    console.print(f"\n[bold cyan]  🤖 Bot:[/bold cyan] {response}")

@click.command()
def main():
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
        report = consultant.saveReport()
        consultant.detectTarget(datasetPath, report)
        console.print()
        console.print(
            Panel(
                "[bold green]✅  Understood! Proceeding automatically...[/bold green]\n[dim]Configuration saved to ./configuration/consultation.json[/dim]",
                border_style="green", padding=(1, 4))
        )
        console.print()
        console.print("[bold magenta]  📋  Generating project plan...[/bold magenta]")
        runEDA(datasetPath)
        planner = Planner()
        planPath = planner.createPlan(datasetPath)
        console.print()
        console.print(
            Panel(
                f"[bold green]✅  Project plan created![/bold green]\n[dim]Plan saved to {planPath}[/dim]",
                border_style="green", padding=(1, 4))
        )
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

    console.print()
    console.print(
        Panel(
            "[bold green]✅  Not any question! Consultation complete![/bold green]\n[dim]Configuration saved to ./configuration/consultation.json[/dim]",
            border_style="green", padding=(1, 4))
    )

    console.print()
    console.print("[bold magenta]  📋  Generating project plan...[/bold magenta]")
    runEDA(datasetPath)
    planner = Planner()
    planPath = planner.createPlan(datasetPath)
    console.print()
    console.print(
        Panel(
            f"[bold green]✅  Project plan created![/bold green]\n[dim]Plan saved to {planPath}[/dim]",
            border_style="green", padding=(1, 4))
    )

if __name__ == "__main__":
    main()