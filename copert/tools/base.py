"""Base tool utilities and helpers."""

from typing import Any, Dict
from langchain_core.tools import tool


class ToolResult:
    """Standardized result format for tool executions."""

    def __init__(self, success: bool, data: Any = None, error: str = None):
        """Initialize a tool result.

        Args:
            success: Whether the tool execution was successful
            data: The result data (if successful)
            error: Error message (if failed)
        """
        self.success = success
        self.data = data
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format.

        Returns:
            Dictionary representation of the result
        """
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
        }

    def __str__(self) -> str:
        """String representation of the result."""
        if self.success:
            return str(self.data) if self.data is not None else "Success"
        return f"Error: {self.error}"


def handle_tool_error(error: Exception) -> str:
    """Standard error handler for tools.

    Args:
        error: The exception that occurred

    Returns:
        Formatted error message
    """
    error_type = type(error).__name__
    return f"{error_type}: {str(error)}"
