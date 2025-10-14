"""Edit tool for performing exact string replacements in files."""

import os
from langchain_core.tools import tool
from pathlib import Path


@tool(parse_docstring=True)
def edit_file(file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> str:
    """Perform exact string replacements in files.

    You must use the Read tool at least once before editing. This tool will error if you attempt
    an edit without reading the file first. When editing text from Read tool output, ensure you
    preserve the exact indentation as it appears AFTER the line number prefix.

    IMPORTANT: Use relative paths for project files (e.g., "src/main.py", "tests/test.py").
    The tool will automatically convert relative paths to absolute paths based on the current working directory.
    When using this tool to remove chunks of code, be aware of surrounding context and associated comments.

    Args:
        file_path: Path to the file to modify (relative to current directory, e.g., "src/main.py")
        old_string: The text to replace (must match exactly including whitespace)
        new_string: The text to replace it with (must be different from old_string)
        replace_all: Replace all occurrences of old_string (default: False)

    Returns:
        Success message with number of replacements, or error message
    """
    try:
        # Convert relative paths to absolute (relative to current working directory)
        file_path = os.path.abspath(file_path)
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            return f"Error: File not found: {file_path}"

        # Check if it's a file
        if not path.is_file():
            return f"Error: Path is not a file: {file_path}"

        # Validate old_string != new_string
        if old_string == new_string:
            return "Error: old_string and new_string must be different"

        # Read file contents
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if old_string exists in the file
        if old_string not in content:
            return f"Error: old_string not found in file: {file_path}"

        # Count occurrences
        occurrences = content.count(old_string)

        # Check for uniqueness if replace_all is False
        if not replace_all and occurrences > 1:
            return (
                f"Error: old_string appears {occurrences} times in the file. "
                "Either provide a larger string with more surrounding context to make it unique, "
                "or use replace_all=True to change every instance."
            )

        # Perform replacement
        if replace_all:
            new_content = content.replace(old_string, new_string)
            replacements = occurrences
        else:
            new_content = content.replace(old_string, new_string, 1)
            replacements = 1

        # Write back to file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return f"Successfully replaced {replacements} occurrence(s) in {file_path}"

    except PermissionError:
        return f"Error: Permission denied: {file_path}"
    except UnicodeDecodeError:
        return f"Error: Unable to decode file (possibly binary): {file_path}"
    except Exception as e:
        return f"Error editing file: {type(e).__name__}: {str(e)}"
