"""Tools module - collection of all available tools for the Copert agent."""

from copert.tools.file_ops import read_file, write_file, edit_file
from copert.tools.file_ops.ls import ls
from copert.tools.file_ops.multiedit import multiedit
from copert.tools.search import grep, glob
from copert.tools.execution import bash
from copert.tools.task_management import todowrite
from copert.tools.web import webfetch, websearch
from copert.tools.base import ToolResult, handle_tool_error

# List of all available tools
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
    "ALL_TOOLS",
    "ToolResult",
    "handle_tool_error",
]
