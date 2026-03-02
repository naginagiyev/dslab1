import click
import questionary
from pathlib import Path
from rich.text import Text
from rich.panel import Panel
from rich.console import Console
from agents.consultant import Consultant

console = Console()

def printBotResponse(response: str):
    console.print(f"\n[bold cyan]  🤖 Bot:[/bold cyan] {response}\n")

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
    initialPrompt = questionary.text("💬  What's your initial prompt?").ask()

    if initialPrompt is None:
        console.print("[yellow]  ⚠️  Cancelled.[/yellow]")
        return

    console.print()
    console.print("[bold magenta]  ❓  Preparing questions...[/bold magenta]\n")

    consultant = Consultant()
    userInput = f"Dataset Path: {datasetPath}\nUser Prompt: {initialPrompt}"

    while True:
        question = consultant.nextQuestion(userInput)

        if question is None:
            break

        printBotResponse(question)

        userInput = questionary.text("💬  You:").ask()

        if userInput is None:
            console.print("[yellow]⚠️  Cancelled.[/yellow]")
            return

    consultant.saveReport()

    console.print()
    console.print(
        Panel(
            "[bold green]✅  Not any question! Consultation complete![/bold green]\n[dim]Configuration saved to ./configuration/consultation.json[/dim]",
            border_style="green", padding=(1, 4))
    )

if __name__ == "__main__":
    main()