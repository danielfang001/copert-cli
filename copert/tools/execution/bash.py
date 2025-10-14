"""Bash tool for executing shell commands."""

import subprocess
from typing import Optional
from langchain_core.tools import tool


@tool(parse_docstring=True)
def bash(command: str, timeout: Optional[int] = 120000, description: Optional[str] = None) -> str:
    """Execute a bash command in a persistent shell session with optional timeout.

    IMPORTANT: This tool is for terminal operations like git, npm, docker, etc.
    DO NOT use it for file operations (reading, writing, editing, searching) - use specialized tools instead.

    Before executing:
    1. Always quote file paths that contain spaces with double quotes
    2. Try to maintain current working directory by using absolute paths and avoiding cd
    3. Use ';' or '&&' to chain commands on a single line (DO NOT use newlines)

    Args:
        command: The bash command to execute
        timeout: Timeout in milliseconds (default: 120000ms = 2 minutes, max: 600000ms = 10 minutes)
        description: Clear, concise description of what this command does (5-10 words)

    Returns:
        Command output (stdout and stderr combined), or error message
    """
    try:
        # Convert timeout from milliseconds to seconds
        timeout_seconds = min(timeout / 1000, 600) if timeout else 120

        # Execute the command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=None,  # Use current working directory
        )

        # Combine stdout and stderr
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            if output:
                output += "\n"
            output += result.stderr

        # Include exit code in output if command failed
        if result.returncode != 0:
            status_msg = f"\n[Command exited with code {result.returncode}]"
            output = (output + status_msg) if output else status_msg

        # Truncate output if it exceeds 30000 characters
        if len(output) > 30000:
            output = output[:30000] + "\n\n[Output truncated - exceeded 30000 characters]"

        return output if output else "[Command completed with no output]"

    except subprocess.TimeoutExpired:
        timeout_min = timeout_seconds / 60
        return f"Error: Command timed out after {timeout_min:.1f} minutes"
    except Exception as e:
        return f"Error executing command: {type(e).__name__}: {str(e)}"
