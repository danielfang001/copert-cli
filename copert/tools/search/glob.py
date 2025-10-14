"""Glob tool - fast file pattern matching."""

import glob as glob_module
from typing import Optional
from langchain_core.tools import tool
from pathlib import Path


@tool(parse_docstring=True)
def glob(pattern: str, path: Optional[str] = None) -> str:
    """Fast file pattern matching tool that works with any codebase size.

    Supports glob patterns and returns matching file paths sorted by modification time.
    Use this tool when you need to find files by name patterns.

    Args:
        pattern: The glob pattern to match files against (e.g., "**/*.js", "src/**/*.ts")
        path: The directory to search in (if not specified, current working directory will be used)

    Returns:
        List of matching file paths (one per line), or error message
    """
    try:
        # Determine the search path
        search_path = Path(path) if path else Path.cwd()

        # Validate the search path exists
        if not search_path.exists():
            return f"Error: Directory not found: {search_path}"

        if not search_path.is_dir():
            return f"Error: Path is not a directory: {search_path}"

        # Perform glob search
        # Use rglob for recursive patterns (**) or glob for non-recursive
        if "**" in pattern:
            # Recursive glob
            matches = list(search_path.glob(pattern))
        else:
            # Non-recursive glob
            full_pattern = str(search_path / pattern)
            matches = [Path(p) for p in glob_module.glob(full_pattern)]

        # Filter out directories, keep only files
        file_matches = [p for p in matches if p.is_file()]

        # Sort by modification time (most recent first)
        file_matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Format results
        if not file_matches:
            return f"No files found matching pattern: {pattern}"

        # Convert to relative paths if they're under the search path
        result_lines = []
        for file_path in file_matches:
            try:
                rel_path = file_path.relative_to(search_path)
                result_lines.append(str(rel_path))
            except ValueError:
                # If relative path fails, use absolute path
                result_lines.append(str(file_path))

        count = len(result_lines)
        header = f"Found {count} file(s) matching '{pattern}':\n"
        return header + "\n".join(result_lines)

    except PermissionError as e:
        return f"Error: Permission denied accessing: {e.filename}"
    except Exception as e:
        return f"Error executing glob: {type(e).__name__}: {str(e)}"
