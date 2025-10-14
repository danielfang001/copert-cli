"""Todo list management tool."""

import json
from typing import List, Dict, Any, Literal
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class TodoWriteInput(BaseModel):
    """Input schema for todowrite tool."""

    todos: List[Dict[str, Any]] = Field(
        description="The updated todo list. Each todo must have: 'content' (string), 'status' (pending/in_progress/completed), and 'id' (unique string)"
    )


@tool(args_schema=TodoWriteInput)
def todowrite(todos: List[Dict[str, Any]]) -> str:
    """Create and manage a structured task list for your current coding session.

    This helps you track progress, organize complex tasks, and demonstrate thoroughness
    to the user. Tasks are executed in order as a simple bullet point list.

    When to Use This Tool:
    1. Complex multi-step tasks - When a task requires 3 or more distinct steps or actions
    2. Non-trivial and complex tasks - Tasks that require careful planning or multiple operations
    3. User explicitly requests todo list - When the user directly asks you to use the todo list
    4. User provides multiple tasks - When users provide a list of things to be done
    5. After receiving new instructions - Immediately capture user requirements as todos
    6. When you start working on a task - Mark it as in_progress BEFORE beginning work
    7. After completing a task - Mark it as completed and add any new follow-up tasks

    When NOT to Use This Tool:
    1. There is only a single, straightforward task
    2. The task is trivial and tracking it provides no organizational benefit
    3. The task can be completed in less than 3 trivial steps
    4. The task is purely conversational or informational

    Task States:
    - pending: Task not yet started
    - in_progress: Currently working on (limit to ONE task at a time)
    - completed: Task finished successfully

    Args:
        todos: The updated todo list. Each todo must have:
            - content: Task description (required, min length 1)
            - status: One of "pending", "in_progress", "completed" (required)
            - id: Unique identifier for the task (required)

    Returns:
        Formatted todo list or error message
    """
    try:
        # Validate todos list
        if not todos or len(todos) == 0:
            return "Error: No todos provided. Must provide at least one todo item."

        # Parse and validate todo items
        todo_items = []
        seen_ids = set()
        in_progress_count = 0

        for i, todo_dict in enumerate(todos):
            try:
                # Validate required fields
                required_fields = ["content", "status", "id"]
                for field in required_fields:
                    if field not in todo_dict:
                        return f"Error: Todo {i+1} missing required field '{field}'"

                content = todo_dict["content"]
                status = todo_dict["status"]
                todo_id = todo_dict["id"]

                # Validate content is not empty
                if not content or len(content.strip()) == 0:
                    return f"Error: Todo {i+1} has empty content"

                # Validate status
                if status not in ["pending", "in_progress", "completed"]:
                    return f"Error: Todo {i+1} has invalid status '{status}'. Must be one of: pending, in_progress, completed"

                # Validate unique ID
                if todo_id in seen_ids:
                    return f"Error: Duplicate todo ID '{todo_id}' found"
                seen_ids.add(todo_id)

                # Count in_progress items
                if status == "in_progress":
                    in_progress_count += 1

                todo_items.append({
                    "content": content,
                    "status": status,
                    "id": todo_id
                })

            except Exception as e:
                return f"Error parsing todo {i+1}: {str(e)}"

        # Warn if more than one task is in_progress
        warning = ""
        if in_progress_count > 1:
            warning = f"\n⚠️  Warning: {in_progress_count} tasks are marked as in_progress. Ideally only ONE task should be in_progress at a time."

        # Format output as ordered list
        result = "📝 Todo List (execute in order):\n\n"

        for i, todo in enumerate(todo_items, 1):
            if todo["status"] == "completed":
                result += f"{i}. ✅ {todo['content']}\n"
            elif todo["status"] == "in_progress":
                result += f"{i}. 🔄 {todo['content']}\n"
            else:  # pending
                result += f"{i}. ⏳ {todo['content']}\n"

        # Summary
        completed_count = len([t for t in todo_items if t["status"] == "completed"])
        in_progress_count = len([t for t in todo_items if t["status"] == "in_progress"])
        pending_count = len([t for t in todo_items if t["status"] == "pending"])

        result += f"\nProgress: {completed_count}/{len(todo_items)} completed"
        result += warning

        return result

    except Exception as e:
        return f"Error in todowrite: {str(e)}"
