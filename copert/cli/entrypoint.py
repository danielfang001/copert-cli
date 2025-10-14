"""CLI entry point for Copert."""

import sys
from copert.cli.main import app
from copert.cli.session import CopertSession


def cli_main():
    """Entry point for the Copert CLI.

    If no arguments are provided, starts an interactive session.
    Otherwise, runs the Typer CLI commands.
    """
    if len(sys.argv) == 1:
        # No arguments - start interactive session
        session = CopertSession()
        session.run()
    else:
        # Arguments provided - run Typer commands
        app()


if __name__ == "__main__":
    cli_main()
