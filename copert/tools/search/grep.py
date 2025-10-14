"""Grep tool - a powerful search tool built on ripgrep."""

import subprocess
from typing import Optional, Literal
from langchain_core.tools import tool


@tool(parse_docstring=True)
def grep(
    pattern: str,
    path: Optional[str] = None,
    glob: Optional[str] = None,
    output_mode: Literal["content", "files_with_matches", "count"] = "files_with_matches",
    case_insensitive: bool = False,
    show_line_numbers: bool = False,
    context_before: Optional[int] = None,
    context_after: Optional[int] = None,
    multiline: bool = False,
) -> str:
    """A powerful search tool built on ripgrep.

    ALWAYS use this tool for search tasks. NEVER invoke grep or rg as a Bash command.
    Supports full regex syntax and provides multiple output modes.

    Args:
        pattern: The regular expression pattern to search for in file contents
        path: File or directory to search in (defaults to current working directory)
        glob: Glob pattern to filter files (e.g., "*.js", "**/*.tsx")
        output_mode: Output mode - "content" shows matching lines, "files_with_matches" shows only file paths, "count" shows match counts
        case_insensitive: Case insensitive search (rg -i flag)
        show_line_numbers: Show line numbers in output (rg -n flag, requires output_mode="content")
        context_before: Number of lines to show before each match (rg -B flag, requires output_mode="content")
        context_after: Number of lines to show after each match (rg -A flag, requires output_mode="content")
        multiline: Enable multiline mode where . matches newlines (rg -U --multiline-dotall)

    Returns:
        Search results based on output_mode, or error message
    """
    try:
        # Build ripgrep command
        cmd = ["rg"]

        # Add pattern
        cmd.append(pattern)

        # Add path if specified
        if path:
            cmd.append(path)

        # Add flags based on parameters
        if case_insensitive:
            cmd.append("-i")

        if multiline:
            cmd.extend(["-U", "--multiline-dotall"])

        # Add glob pattern if specified
        if glob:
            cmd.extend(["--glob", glob])

        # Configure output mode
        if output_mode == "files_with_matches":
            cmd.append("-l")  # List files with matches
        elif output_mode == "count":
            cmd.append("-c")  # Show count per file
        elif output_mode == "content":
            if show_line_numbers:
                cmd.append("-n")
            if context_before is not None:
                cmd.extend(["-B", str(context_before)])
            if context_after is not None:
                cmd.extend(["-A", str(context_after)])

        # Execute ripgrep
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
        )

        # ripgrep returns exit code 1 when no matches found, which is not an error
        if result.returncode == 0:
            output = result.stdout.strip()
            if not output:
                return "No matches found"
            return output
        elif result.returncode == 1:
            return "No matches found"
        else:
            # Other non-zero exit codes indicate errors
            error_msg = result.stderr.strip() or "Unknown error occurred"
            return f"Error executing ripgrep: {error_msg}"

    except FileNotFoundError:
        return (
            "Error: ripgrep (rg) not found. Please install ripgrep:\n"
            "  - macOS: brew install ripgrep\n"
            "  - Linux: apt install ripgrep or yum install ripgrep\n"
            "  - Windows: choco install ripgrep"
        )
    except subprocess.TimeoutExpired:
        return "Error: Search timed out after 30 seconds"
    except Exception as e:
        return f"Error executing grep: {type(e).__name__}: {str(e)}"
