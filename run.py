import os
import click
import questionary
from pathlib import Path
from rich.text import Text
from path import promptsDir
from rich.panel import Panel
from rich.console import Console
from models.generation import GenerationModel

console = Console()

def printBotResponse(response: str):
    console.print(f"\n[bold cyan]🤖 Bot:[/bold cyan] {response}\n")

@click.command()
def main():
    text = Text()
    text.append("🤖  Agentic Machine Learning Automation", style="bold cyan")
    console.print(Panel(text, border_style="cyan", padding=(1, 4)))
    console.print()

    while True:
        datasetPath = questionary.path("📂  Path to your dataset:", only_directories=False).ask()

        if datasetPath is None:
            console.print("[yellow]⚠️  Cancelled.[/yellow]")
            return

        if not Path(datasetPath).exists():
            console.print("[red]❌  I don't see a dataset at that path. Are you sure you entered it right?[/red]\n")
            continue
        break

    console.print(f"[green]✅  Dataset loaded:[/green] [dim]{datasetPath}[/dim]\n")
    initialPrompt = questionary.text("💬  What's your initial prompt?").ask()

    if initialPrompt is None:
        console.print("[yellow]⚠️  Cancelled.[/yellow]")
        return

    console.print()
    consultantAgent = GenerationModel(os.path.join(promptsDir, "consultant.md"))
    consultationHistory = []
    sentInitialPrompt = False

    console.print("[bold magenta]🚀  Starting consultation...[/bold magenta]\n")

    while True:
        if not sentInitialPrompt:
            sentInitialPrompt = True
            userInput = f"Dataset Path: {datasetPath}, Prompt: {initialPrompt}"
        else:
            userInput = questionary.text("💬  You:").ask()

            if userInput is None:
                console.print("[yellow]⚠️  Cancelled.[/yellow]")
                break

        response = consultantAgent.generate(query=userInput, history=consultationHistory)

        if response == "Ready to Proceed!":
            break

        printBotResponse(response)

    console.print()
    console.print(
        Panel(
            "[bold green]✅  Our consultation is over![/bold green]\n[dim]Thanks for using Consultant AI 🎉[/dim]",
            border_style="green", padding=(1, 4))
    )

if __name__ == "__main__":
    main()