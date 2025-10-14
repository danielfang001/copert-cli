"""Main CLI entry point for Copert."""

import typer
from rich.console import Console
from rich.markdown import Markdown
from pathlib import Path

from copert.agents import invoke_agent
from copert.config import settings

app = typer.Typer(
    name="copert",
    help="AI-powered coding assistant CLI",
    add_completion=False,
)
console = Console()


@app.command()
def chat(
    message: str = typer.Argument(..., help="Your message to the coding assistant"),
):
    """Chat with the Copert AI coding assistant.

    Examples:
        copert chat "Can you help me write a Python function?"
        copert chat "Read the main.py file and explain what it does"
    """
    try:
        # Display user message
        console.print("\n[bold cyan]You:[/bold cyan]", message)
        console.print()

        # Invoke the agent
        with console.status("[bold green]Thinking...", spinner="dots"):
            result = invoke_agent(message)

        # Extract the final AI response
        messages = result["messages"]
        final_response = messages[-1]

        # Display assistant response
        console.print("[bold green]Copert:[/bold green]")

        if hasattr(final_response, 'content') and final_response.content:
            # Render as markdown
            md = Markdown(final_response.content)
            console.print(md)
        else:
            console.print("[dim]No response generated[/dim]")

        console.print()

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def version():
    """Display the version of Copert CLI."""
    console.print("[bold]Copert CLI[/bold] version 0.1.0")


@app.command()
def config():
    """Display current configuration."""
    console.print("\n[bold]Current Configuration:[/bold]\n")
    console.print(f"Model: {settings.openai_model}")
    console.print(f"Temperature: {settings.openai_temperature}")
    console.print(f"Max Tokens: {settings.openai_max_tokens}")
    console.print(f"Max Iterations: {settings.max_iterations}")
    console.print()


if __name__ == "__main__":
    app()
