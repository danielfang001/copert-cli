"""Memory management utilities for loading COPERT.md context files."""

import os
from pathlib import Path
from typing import Optional


def load_copert_md(cwd: Optional[str] = None) -> Optional[str]:
    """Load COPERT.md file if it exists in the current working directory.

    Similar to Claude Code's CLAUDE.md loading mechanism, this function:
    1. Checks for COPERT.md in the current working directory
    2. Returns the content if found, None otherwise

    Args:
        cwd: Current working directory (defaults to os.getcwd())

    Returns:
        Content of COPERT.md if found, None otherwise
    """
    if cwd is None:
        cwd = os.getcwd()

    copert_path = Path(cwd) / "COPERT.md"

    if copert_path.exists() and copert_path.is_file():
        try:
            with open(copert_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            # Silently fail if we can't read the file
            return None

    return None


def format_copert_context(content: str) -> str:
    """Format COPERT.md content for inclusion in system context.

    Args:
        content: Raw COPERT.md content

    Returns:
        Formatted content ready to be added to system prompt
    """
    return f"""

# Project Context (from COPERT.md)

The following information provides project-specific context loaded from COPERT.md:

{content}

---

Use the above project context to better understand this codebase and provide more accurate assistance.
"""
