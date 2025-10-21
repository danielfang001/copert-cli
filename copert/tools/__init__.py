"""Tools module - collection of all available tools for the Copert agent."""

from copert.tools.file_ops import read_file, write_file, edit_file
from copert.tools.file_ops.ls import ls
from copert.tools.file_ops.multiedit import multiedit
from copert.tools.search import grep, glob
from copert.tools.execution import bash
from copert.tools.task_management import todowrite
from copert.tools.web import webfetch, websearch
from copert.tools.task import task
from copert.tools.project import init, write_copert_md, read_copert_md
from copert.tools.base import ToolResult, handle_tool_error

# Read-only tools for general-purpose sub-agent (research and analysis)
READ_ONLY_TOOLS = [
    read_file,
    ls,
    grep,
    glob,
    webfetch,
    websearch,
]

# Code implementation tools for code-writer sub-agent (can write/edit but not execute)
CODE_WRITER_TOOLS = [
    read_file,
    write_file,
    edit_file,
    multiedit,
    ls,
    grep,
    glob,
]

# Project initialization tools for project-init sub-agent (read, write, search - no execution)
PROJECT_INIT_TOOLS = [
    read_file,
    write_file,
    ls,
    grep,
    glob,
    write_copert_md,  # Dedicated tool for writing COPERT.md to project root
    read_copert_md,   # Dedicated tool for reading existing COPERT.md
]

# List of all available tools for main agent
ALL_TOOLS = [
    read_file,
    write_file,
    edit_file,
    ls,
    multiedit,
    grep,
    glob,
    bash,
    todowrite,
    webfetch,
    websearch,
    task,
    init,
]

__all__ = [
    "read_file",
    "write_file",
    "edit_file",
    "ls",
    "multiedit",
    "grep",
    "glob",
    "bash",
    "todowrite",
    "webfetch",
    "websearch",
    "task",
    "init",
    "ALL_TOOLS",
    "READ_ONLY_TOOLS",
    "CODE_WRITER_TOOLS",
    "PROJECT_INIT_TOOLS",
    "ToolResult",
    "handle_tool_error",
]
