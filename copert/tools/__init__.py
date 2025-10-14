"""Tools module - collection of all available tools for the Copert agent."""

from copert.tools.file_ops import read_file, write_file, edit_file
from copert.tools.file_ops.ls import ls
from copert.tools.file_ops.multiedit import multiedit
from copert.tools.search import grep, glob
from copert.tools.execution import bash
from copert.tools.task_management import todowrite
from copert.tools.web import webfetch, websearch
from copert.tools.task import task
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
    "ALL_TOOLS",
    "READ_ONLY_TOOLS",
    "CODE_WRITER_TOOLS",
    "ToolResult",
    "handle_tool_error",
]
