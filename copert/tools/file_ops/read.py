"""Read tool for reading files from the filesystem."""

import os
from typing import Optional
from langchain_core.tools import tool
from pathlib import Path


@tool(parse_docstring=True)
def read_file(file_path: str, offset: Optional[int] = None, limit: Optional[int] = None) -> str:
    """Read a file from the local filesystem.

    This tool reads files and returns their contents with line numbers.
    By default, it reads up to 2000 lines starting from the beginning.

    IMPORTANT: Use relative paths for project files (e.g., "src/main.py", "README.md").
    The tool will automatically convert relative paths to absolute paths based on the current working directory.

    Args:
        file_path: Path to the file to read (relative to current directory, e.g., "src/main.py")
        offset: The line number to start reading from (optional)
        limit: The number of lines to read (optional, default 2000)

    Returns:
        File contents with line numbers in cat -n format, or error message
    """
    try:
        # Convert relative paths to absolute (relative to current working directory)
        file_path = os.path.abspath(file_path)
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            return f"Error: File not found: {file_path}"

        # Check if it's a file (not a directory)
        if not path.is_file():
            return f"Error: Path is not a file: {file_path}"

        # Read file contents
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        # Apply offset and limit
        start = (offset - 1) if offset else 0
        end = start + limit if limit else None
        selected_lines = lines[start:end]

        # Format with line numbers (cat -n style)
        formatted_lines = []
        for i, line in enumerate(selected_lines, start=start + 1):
            # Truncate lines longer than 2000 characters
            if len(line) > 2000:
                line = line[:2000] + "... [truncated]\n"
            formatted_lines.append(f"{i:6d}\t{line.rstrip()}")

        result = "\n".join(formatted_lines)

        # Add metadata about the read operation
        total_lines = len(lines)
        lines_read = len(selected_lines)
        metadata = f"[Read {lines_read} of {total_lines} total lines"
        if offset:
            metadata += f", starting from line {offset}"
        metadata += "]"

        return f"{metadata}\n\n{result}" if result else f"{metadata}\n\n[File is empty]"

    except PermissionError:
        return f"Error: Permission denied: {file_path}"
    except UnicodeDecodeError:
        return f"Error: Unable to decode file (possibly binary): {file_path}"
    except Exception as e:
        return f"Error reading file: {type(e).__name__}: {str(e)}"
