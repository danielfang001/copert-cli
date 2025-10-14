"""Multiple file edit tool."""

import os
from typing import List, Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class EditOperation(BaseModel):
    """Single edit operation."""

    old_string: str = Field(description="The text to replace")
    new_string: str = Field(description="The text to replace it with")
    replace_all: bool = Field(default=False, description="Replace all occurrences of old_string (default false)")


class MultiEditInput(BaseModel):
    """Input schema for multiedit tool."""

    file_path: str = Field(description="Path to the file to modify (relative to current directory, e.g., 'src/main.py')")
    edits: List[Dict[str, Any]] = Field(
        description="Array of edit operations to perform sequentially. Each edit must contain 'old_string' and 'new_string', and optionally 'replace_all' (boolean)"
    )


@tool(args_schema=MultiEditInput)
def multiedit(file_path: str, edits: List[Dict[str, Any]]) -> str:
    """Make multiple edits to a single file in one operation.

    This tool is built on top of the Edit tool and allows you to perform multiple
    find-and-replace operations efficiently. Prefer this tool over the Edit tool
    when you need to make multiple edits to the same file.

    Before using this tool:
    1. Use the Read tool to understand the file's contents and context
    2. Verify the directory path is correct

    IMPORTANT - Path Handling:
    - Use relative paths for project files (e.g., "src/main.py", "tests/test.py")
    - The tool will automatically convert relative paths to absolute paths based on the current working directory
    - Never use absolute paths starting with "/" unless referring to files outside the project

    IMPORTANT - Edit Behavior:
    - All edits are applied in sequence, in the order they are provided
    - Each edit operates on the result of the previous edit
    - All edits must be valid for the operation to succeed - if any edit fails, none will be applied
    - This tool is ideal when you need to make several changes to different parts of the same file

    CRITICAL REQUIREMENTS:
    1. All edits follow the same requirements as the single Edit tool
    2. The edits are atomic - either all succeed or none are applied
    3. Plan your edits carefully to avoid conflicts between sequential operations

    WARNING:
    - The tool will fail if old_string doesn't match the file contents exactly (including whitespace)
    - The tool will fail if old_string and new_string are the same
    - Since edits are applied in sequence, ensure that earlier edits don't affect the text that later edits are trying to find

    When making edits:
    - Ensure all edits result in idiomatic, correct code
    - Do not leave the code in a broken state
    - Use replace_all for replacing and renaming strings across the file

    Args:
        file_path: Path to the file to modify (relative to current directory, e.g., "src/main.py")
        edits: Array of edit operations to perform sequentially on the file. Each edit contains:
            - old_string: The text to replace
            - new_string: The text to replace it with
            - replace_all: Replace all occurrences (optional, default false)

    Returns:
        Success message with edit count, or error message
    """
    try:
        # Convert relative paths to absolute (relative to current working directory)
        file_path = os.path.abspath(file_path)

        # Validate file path is absolute (should always be true after abspath)
        if not os.path.isabs(file_path):
            return f"Error: File path must be absolute, not relative. Got: {file_path}"

        # Check if file exists
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"

        # Check if path is a file
        if not os.path.isfile(file_path):
            return f"Error: Path is not a file: {file_path}"

        # Validate edits
        if not edits or len(edits) == 0:
            return "Error: No edits provided. Must provide at least one edit operation."

        # Parse edit operations
        edit_operations = []
        for i, edit_dict in enumerate(edits):
            try:
                # Validate required fields
                if "old_string" not in edit_dict:
                    return f"Error: Edit {i+1} missing required field 'old_string'"
                if "new_string" not in edit_dict:
                    return f"Error: Edit {i+1} missing required field 'new_string'"

                old_string = edit_dict["old_string"]
                new_string = edit_dict["new_string"]
                replace_all = edit_dict.get("replace_all", False)

                # Validate that old_string and new_string are different
                if old_string == new_string:
                    return f"Error: Edit {i+1} has identical old_string and new_string"

                edit_operations.append({
                    "old_string": old_string,
                    "new_string": new_string,
                    "replace_all": replace_all
                })
            except Exception as e:
                return f"Error parsing edit {i+1}: {str(e)}"

        # Read the file
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            return f"Error: File is not a valid UTF-8 text file: {file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

        # Store original content for rollback
        original_content = content

        # Apply edits sequentially
        for i, edit in enumerate(edit_operations):
            old_string = edit["old_string"]
            new_string = edit["new_string"]
            replace_all = edit["replace_all"]

            # Check if old_string exists in current content
            if old_string not in content:
                return f"Error: Edit {i+1} failed - old_string not found in file (remember edits are applied sequentially)"

            # Check uniqueness if not replace_all
            if not replace_all and content.count(old_string) > 1:
                count = content.count(old_string)
                return f"Error: Edit {i+1} failed - old_string appears {count} times in file. Use replace_all=true to replace all occurrences, or provide more context to make it unique."

            # Apply the edit
            if replace_all:
                content = content.replace(old_string, new_string)
            else:
                # Replace only first occurrence
                content = content.replace(old_string, new_string, 1)

        # Write the modified content back to the file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            # Try to restore original content
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(original_content)
            except:
                pass
            return f"Error writing file: {str(e)}"

        # Calculate statistics
        lines_changed = len([line for line in content.split("\n")])

        return f"Successfully applied {len(edit_operations)} edits to {file_path} ({lines_changed} lines total)"

    except Exception as e:
        return f"Error in multiedit: {str(e)}"
