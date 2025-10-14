"""Pydantic schemas for tool parameters and data validation."""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


# File Operations Schemas
class ReadToolInput(BaseModel):
    """Input schema for Read tool."""

    file_path: str = Field(description="The absolute path to the file to read")
    offset: Optional[int] = Field(
        default=None,
        description="The line number to start reading from"
    )
    limit: Optional[int] = Field(
        default=None,
        description="The number of lines to read"
    )


class WriteToolInput(BaseModel):
    """Input schema for Write tool."""

    file_path: str = Field(description="The absolute path to the file to write")
    content: str = Field(description="The content to write to the file")


class EditToolInput(BaseModel):
    """Input schema for Edit tool."""

    file_path: str = Field(description="The absolute path to the file to modify")
    old_string: str = Field(description="The text to replace")
    new_string: str = Field(description="The text to replace it with")
    replace_all: bool = Field(
        default=False,
        description="Replace all occurrences of old_string"
    )


# Search Schemas
class GrepToolInput(BaseModel):
    """Input schema for Grep tool."""

    pattern: str = Field(description="The regular expression pattern to search for")
    path: Optional[str] = Field(
        default=None,
        description="File or directory to search in"
    )
    glob: Optional[str] = Field(
        default=None,
        description="Glob pattern to filter files (e.g., '*.js', '*.{ts,tsx}')"
    )
    output_mode: Literal["content", "files_with_matches", "count"] = Field(
        default="files_with_matches",
        description="Output mode"
    )
    case_insensitive: bool = Field(
        default=False,
        description="Case insensitive search (-i flag)"
    )
    show_line_numbers: bool = Field(
        default=False,
        description="Show line numbers in output (-n flag)"
    )
    context_before: Optional[int] = Field(
        default=None,
        description="Number of lines to show before each match (-B flag)"
    )
    context_after: Optional[int] = Field(
        default=None,
        description="Number of lines to show after each match (-A flag)"
    )
    multiline: bool = Field(
        default=False,
        description="Enable multiline mode"
    )


class GlobToolInput(BaseModel):
    """Input schema for Glob tool."""

    pattern: str = Field(description="The glob pattern to match files against")
    path: Optional[str] = Field(
        default=None,
        description="The directory to search in"
    )


# Execution Schemas
class BashToolInput(BaseModel):
    """Input schema for Bash tool."""

    command: str = Field(description="The bash command to execute")
    timeout: Optional[int] = Field(
        default=120000,
        description="Timeout in milliseconds (default: 120000)"
    )
    description: Optional[str] = Field(
        default=None,
        description="Clear, concise description of what this command does"
    )


# Web Schemas
class WebFetchToolInput(BaseModel):
    """Input schema for WebFetch tool."""

    url: str = Field(description="The URL to fetch content from")
    prompt: str = Field(description="The prompt to run on the fetched content")


class WebSearchToolInput(BaseModel):
    """Input schema for WebSearch tool."""

    query: str = Field(description="The search query to use")
    allowed_domains: Optional[List[str]] = Field(
        default=None,
        description="Only include search results from these domains"
    )
    blocked_domains: Optional[List[str]] = Field(
        default=None,
        description="Never include search results from these domains"
    )


# Task Management Schemas
class TodoItem(BaseModel):
    """Schema for a single todo item."""

    content: str = Field(description="The todo item content")
    status: Literal["pending", "in_progress", "completed"] = Field(
        description="The status of the todo"
    )
    activeForm: str = Field(description="The present continuous form of the content")


class TodoWriteToolInput(BaseModel):
    """Input schema for TodoWrite tool."""

    todos: List[TodoItem] = Field(description="The updated todo list")


class TaskToolInput(BaseModel):
    """Input schema for Task tool."""

    description: str = Field(description="A short (3-5 word) description of the task")
    prompt: str = Field(description="The task for the agent to perform")
    subagent_type: str = Field(description="The type of specialized agent to use")
