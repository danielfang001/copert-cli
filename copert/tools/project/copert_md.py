"""Dedicated tools for reading and writing COPERT.md files."""

import os
from pathlib import Path
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class WriteCopertMdInput(BaseModel):
    """Input schema for write_copert_md tool."""
    content: str = Field(description="The content to write to COPERT.md")


class ReadCopertMdInput(BaseModel):
    """Input schema for read_copert_md tool."""
    pass  # No parameters needed


@tool(args_schema=WriteCopertMdInput)
def write_copert_md(content: str) -> str:
    """Write content to COPERT.md in the project root directory.

    This tool ensures COPERT.md is always created in the correct location
    (current working directory root) regardless of where the agent is operating.

    COPERT.md is a project-specific context file that gets automatically loaded
    by Copert CLI to provide better, project-aware assistance.

    Args:
        content: The content to write to COPERT.md. Should start with:
                 # COPERT.md

                 This file provides guidance to Copert CLI when working with code in this repository.

    Returns:
        Success message with file stats or error message
    """
    try:
        # Always write to COPERT.md in current working directory root
        file_path = os.path.join(os.getcwd(), "COPERT.md")
        path = Path(file_path)

        # Write the file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Get file stats
        lines = content.count('\n') + 1 if content else 0
        chars = len(content)

        return f"✅ Successfully wrote COPERT.md to {file_path}\n({lines} lines, {chars} characters)\n\nThis file will be automatically loaded in future Copert sessions."

    except PermissionError:
        return f"Error: Permission denied writing to {file_path}"
    except OSError as e:
        return f"Error: Unable to write COPERT.md: {type(e).__name__}: {str(e)}"
    except Exception as e:
        return f"Error writing COPERT.md: {type(e).__name__}: {str(e)}"


@tool(args_schema=ReadCopertMdInput)
def read_copert_md() -> str:
    """Read the COPERT.md file from the project root directory.

    This tool reads the existing COPERT.md file if it exists, allowing you to
    check what context is already documented or to update it.

    Returns:
        Contents of COPERT.md with line numbers, or error message if not found
    """
    try:
        # Always read from COPERT.md in current working directory root
        file_path = os.path.join(os.getcwd(), "COPERT.md")
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            return f"COPERT.md not found in {os.getcwd()}\n\nYou can create one using the init tool or write_copert_md tool."

        # Check if it's a file (not a directory)
        if not path.is_file():
            return f"Error: COPERT.md exists but is not a file: {file_path}"

        # Read file contents
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        # Format with line numbers (cat -n style)
        formatted_lines = []
        for i, line in enumerate(lines, start=1):
            # Truncate lines longer than 2000 characters
            if len(line) > 2000:
                line = line[:2000] + "... [truncated]\n"
            formatted_lines.append(f"{i:6d}\t{line.rstrip()}")

        result = "\n".join(formatted_lines)
        total_lines = len(lines)

        return f"[Read COPERT.md from {file_path} - {total_lines} lines]\n\n{result}"

    except PermissionError:
        return f"Error: Permission denied reading {file_path}"
    except UnicodeDecodeError:
        return f"Error: Unable to decode COPERT.md (possibly binary): {file_path}"
    except Exception as e:
        return f"Error reading COPERT.md: {type(e).__name__}: {str(e)}"
