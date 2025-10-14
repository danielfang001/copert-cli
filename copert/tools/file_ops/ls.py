"""Directory listing tool."""

import os
from pathlib import Path
from typing import Optional, List
from fnmatch import fnmatch
from langchain_core.tools import tool


@tool(parse_docstring=True)
def ls(path: str, ignore: Optional[List[str]] = None) -> str:
    """List files and directories in a given path.

    This tool provides a formatted list of files and directories with type indicators.
    You can optionally provide an array of glob patterns to ignore with the ignore parameter.
    You should generally prefer the Glob and Grep tools, if you know which directories to search.

    IMPORTANT: Use relative paths for project directories (e.g., ".", "src", "tests").
    The tool will automatically convert relative paths to absolute paths based on the current working directory.
    Never use absolute paths starting with "/" unless referring to directories outside the project.

    Args:
        path: Path to the directory to list (relative to current directory, e.g., ".", "src", "tests")
        ignore: List of glob patterns to ignore (optional, e.g., ["*.pyc", "__pycache__", ".git"])

    Returns:
        Formatted list of files and directories, or error message
    """
    try:
        # Convert relative paths to absolute (relative to current working directory)
        path = os.path.abspath(path)

        # Validate that path is absolute (should always be true after abspath)
        if not os.path.isabs(path):
            return f"Error: Path must be absolute, not relative. Got: {path}"

        # Check if path exists
        if not os.path.exists(path):
            return f"Error: Path does not exist: {path}"

        # Check if path is a directory
        if not os.path.isdir(path):
            return f"Error: Path is not a directory: {path}"

        # Get all entries
        path_obj = Path(path)
        entries = []

        try:
            for entry in path_obj.iterdir():
                # Check if entry should be ignored
                if ignore:
                    should_ignore = False
                    for pattern in ignore:
                        if fnmatch(entry.name, pattern):
                            should_ignore = True
                            break
                    if should_ignore:
                        continue

                # Format entry with type indicator
                if entry.is_dir():
                    entries.append(f"{entry.name}/")
                elif entry.is_symlink():
                    entries.append(f"{entry.name}@")
                else:
                    entries.append(entry.name)
        except PermissionError:
            return f"Error: Permission denied to read directory: {path}"

        # Sort entries: directories first, then files, both alphabetically
        dirs = sorted([e for e in entries if e.endswith('/')])
        files = sorted([e for e in entries if not e.endswith('/')])
        sorted_entries = dirs + files

        # Format output
        if not sorted_entries:
            return f"Directory is empty: {path}"

        result = f"Contents of {path}:\n"
        result += "\n".join(sorted_entries)
        result += f"\n\nTotal: {len(dirs)} directories, {len(files)} files"

        return result

    except Exception as e:
        return f"Error listing directory: {str(e)}"
