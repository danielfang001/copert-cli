"""Task delegation tool for spawning specialized sub-agents."""

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field


class TaskInput(BaseModel):
    """Input schema for task delegation tool."""

    description: str = Field(description="A short (3-5 word) description of the task")
    prompt: str = Field(description="The task for the agent to perform. Be detailed and specific about what you want the sub-agent to do and what information to return.")
    subagent_type: str = Field(description="The type of specialized agent to use for this task. Currently supported: 'general-purpose', 'code-writer'")


@tool(args_schema=TaskInput)
def task(description: str, prompt: str, subagent_type: str) -> str:
    """Launch a new agent to handle complex, multi-step tasks autonomously.

    This tool spawns a specialized sub-agent with a fresh context to handle complex operations
    like extensive codebase searches, multi-file analysis, or research tasks.

    Available agent types:
    - **general-purpose**: Research and analysis specialist with read-only access.
      Tools: read_file, ls, grep, glob, webfetch, websearch
      Use for: Codebase searches, pattern analysis, documentation research

    - **code-writer**: Code implementation specialist with write access but no execution.
      Tools: read_file, write_file, edit_file, multiedit, ls, grep, glob
      Use for: Implementing changes across multiple files, refactoring, code generation

    When to use this tool:
    - **general-purpose**: Multiple search operations, pattern analysis, research
    - **code-writer**: Implementing features, bulk refactoring, multi-file changes
    - Task requires isolation to prevent context pollution
    - Complex multi-step operations that benefit from specialization

    When NOT to use this tool:
    - Reading 1-3 specific known files (use read_file instead)
    - Simple single-file edits (use edit_file directly)
    - Tasks requiring test execution or verification (handle in main agent)

    Important notes:
    - Sub-agent starts with fresh context (not burdened by conversation history)
    - Sub-agent is stateless - no follow-up conversations possible
    - Your prompt should be highly detailed with specific instructions
    - Clearly specify what information the sub-agent should return
    - Sub-agent has read-only access (cannot make changes)
    - Sub-agent output is for you (main agent), not the user

    Example usage:
    ```python
    task(
        description="Search API endpoints",
        prompt=\"""
        Search the entire codebase for all API endpoint definitions.
        Look for:
        - FastAPI route decorators (@app.get, @app.post, etc.)
        - Flask route decorators (@app.route)
        - Django URL patterns

        For each endpoint found, report:
        - File path and line number
        - HTTP method
        - Endpoint path
        - Function name

        Return a structured list organized by file.
        \""",
        subagent_type="general-purpose"
    )
    ```

    Args:
        description: Short description of the task (3-5 words)
        prompt: Detailed instructions for the sub-agent
        subagent_type: Type of sub-agent to use ('general-purpose')

    Returns:
        Sub-agent's final report as a string
    """
    # Import here to avoid circular dependency
    from copert.agents.graph import create_agent_graph
    from copert.llm.prompts import GENERAL_PURPOSE_SUBAGENT_PROMPT, CODE_WRITER_SUBAGENT_PROMPT
    from copert.tools import READ_ONLY_TOOLS, CODE_WRITER_TOOLS

    # Validate subagent_type
    valid_types = ["general-purpose", "code-writer"]
    if subagent_type not in valid_types:
        return f"Error: Invalid subagent_type '{subagent_type}'. Valid types: {', '.join(valid_types)}"

    # Select appropriate system prompt and tools based on subagent_type
    if subagent_type == "general-purpose":
        system_prompt = GENERAL_PURPOSE_SUBAGENT_PROMPT
        tools = READ_ONLY_TOOLS
    elif subagent_type == "code-writer":
        system_prompt = CODE_WRITER_SUBAGENT_PROMPT
        tools = CODE_WRITER_TOOLS
    else:
        return f"Error: Subagent type '{subagent_type}' not implemented"

    try:
        # Create a fresh sub-agent graph with specialized prompt and tools
        subagent_graph = create_agent_graph(
            system_prompt=system_prompt,
            tools=tools
        )

        # Create fresh message for sub-agent
        messages = [HumanMessage(content=prompt)]

        # Invoke sub-agent and wait for completion
        result = subagent_graph.invoke({"messages": messages})

        # Extract final AI response
        final_messages = result["messages"]

        # Find the last AI message (the final report)
        for msg in reversed(final_messages):
            if hasattr(msg, 'content') and msg.content:
                return msg.content

        return "Error: Sub-agent did not return a final report"

    except Exception as e:
        return f"Error executing sub-agent: {type(e).__name__}: {str(e)}"
