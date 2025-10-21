"""Project initialization tool for generating COPERT.md context file."""

from langchain_core.tools import tool
from pydantic import BaseModel


class InitInput(BaseModel):
    """Input schema for init tool."""
    pass  # No parameters needed


@tool(args_schema=InitInput)
def init() -> str:
    """Initialize project with COPERT.md guide file.

    This tool spawns a specialized sub-agent that analyzes the codebase and creates
    a COPERT.md file. This file serves as token-efficient context for future Copert sessions,
    similar to how Claude Code uses CLAUDE.md.

    The sub-agent will:
    1. Read README.md and pyproject.toml to understand the project
    2. Analyze project architecture by exploring key files
    3. Create COPERT.md with:
       - Development commands (build, test, lint, run)
       - High-level architecture and patterns
       - Important implementation details
       - Common workflows and best practices

    When to use:
    - First time setting up Copert in a new project
    - After major architectural changes
    - To update project context for better Copert performance

    Returns:
        Success message with path to created COPERT.md file
    """
    # Import here to avoid circular dependency
    from copert.agents.graph import create_agent_graph
    from copert.llm.prompts import PROJECT_INIT_SUBAGENT_PROMPT
    from copert.tools import PROJECT_INIT_TOOLS
    from langchain_core.messages import HumanMessage

    # Create the init prompt
    init_prompt = """Please analyze this codebase and create a COPERT.md file in the project root.

What to include:
1. Commands that will be commonly used, such as how to build, lint, and run tests. Include the necessary commands to develop in this codebase, such as how to run a single test.
2. High-level code architecture and structure so that future instances can be productive more quickly. Focus on the "big picture" architecture that requires reading multiple files to understand.

Usage notes:
- If there's already a COPERT.md, read it and suggest improvements to it by rewriting it.
- When you make the initial COPERT.md, do not repeat yourself and do not include obvious instructions like "Provide helpful error messages to users", "Write unit tests for all new utilities", "Never include sensitive information (API keys, tokens) in code or commits".
- Avoid listing every component or file structure that can be easily discovered.
- Don't include generic development practices.
- If there is a README.md, make sure to include the important parts.
- Do not make up information such as "Common Development Tasks", "Tips for Development", "Support and Documentation" unless this is expressly included in other files that you read.
- Be sure to prefix the file with the following text:

```
# COPERT.md

This file provides guidance to Copert CLI when working with code in this repository.
```

IMPORTANT: Use the write_copert_md(content) tool to create COPERT.md. This tool ensures the file is written to the correct location in the project root.

**YOU MUST CALL write_copert_md(content) AS YOUR FINAL TOOL CALL.** Do not just output the COPERT.md content in your response text - you must actually write it using the tool.

Workflow:
1. Check if COPERT.md exists (read_copert_md)
2. Read README.md and pyproject.toml
3. Explore architecture
4. **WRITE COPERT.md using write_copert_md(content)** ← Required!
5. Provide brief confirmation

Start by checking if COPERT.md already exists using read_copert_md(). If it exists, read it and create an improved version. Then read README.md and pyproject.toml (or package.json, or equivalent dependency files) to understand the project, explore the architecture, and FINALLY call write_copert_md() to save the file."""

    try:
        # Create a fresh sub-agent graph for project initialization
        subagent_graph = create_agent_graph(
            system_prompt=PROJECT_INIT_SUBAGENT_PROMPT,
            tools=PROJECT_INIT_TOOLS
        )

        # Create message for sub-agent
        messages = [HumanMessage(content=init_prompt)]

        # Invoke sub-agent with recursion limit
        result = subagent_graph.invoke(
            {"messages": messages},
            config={"recursion_limit": 50}
        )

        # Extract final AI response
        final_messages = result["messages"]

        import os
        from langchain_core.messages import AIMessage

        # Check if COPERT.md was created
        if os.path.exists("COPERT.md"):
            return "✅ Successfully created COPERT.md\n\nThis file will be automatically loaded as context in all future Copert sessions to provide better, project-aware assistance."

        # Find the last AI message with content for error reporting
        for msg in reversed(final_messages):
            if isinstance(msg, AIMessage) and msg.content:
                return f"⚠️  Init completed but COPERT.md was not found.\n\nThe sub-agent may not have called write_copert_md tool. Please try running /init again.\n\nSub-agent's final message:\n{msg.content[:500]}..."

        return "⚠️  Sub-agent completed but did not return a response. Please try running /init again."

    except Exception as e:
        return f"Error during project initialization: {type(e).__name__}: {str(e)}"
