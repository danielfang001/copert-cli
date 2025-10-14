"""Write tool for writing files to the filesystem."""

import os
from langchain_core.tools import tool
from pathlib import Path


@tool(parse_docstring=True)
def write_file(file_path: str, content: str) -> str:
    """Write a file to the local filesystem.

    This tool will overwrite the existing file if there is one at the provided path.
    ALWAYS prefer editing existing files in the codebase. NEVER write new files unless explicitly required.

    IMPORTANT: Use relative paths for project files (e.g., "src/main.py", "tests/test.py").
    The tool will automatically convert relative paths to absolute paths based on the current working directory.
    Never use absolute paths starting with "/" unless referring to files outside the project.

    Args:
        file_path: Path to the file to write (relative to current directory, e.g., "src/main.py")
        content: The content to write to the file

    Returns:
        Success message or error message
    """
    try:
        # Convert relative paths to absolute (relative to current working directory)
        file_path = os.path.abspath(file_path)
        path = Path(file_path)

        # Ensure the parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write the file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Get file stats
        lines = content.count('\n') + 1 if content else 0
        chars = len(content)

        return f"Successfully wrote to {file_path} ({lines} lines, {chars} characters)"

    except PermissionError:
        return f"Error: Permission denied: {file_path}"
    except OSError as e:
        return f"Error: Unable to write file: {type(e).__name__}: {str(e)}"
    except Exception as e:
        return f"Error writing file: {type(e).__name__}: {str(e)}"
