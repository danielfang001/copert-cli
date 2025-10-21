# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Copert CLI is an AI coding assistant built with LangGraph and OpenAI, adapted from Claude Code. It's a Python CLI tool that provides an interactive REPL for software engineering tasks with multi-agent orchestration.

## Development Commands

### Setup and Installation
```bash
# Install dependencies
uv sync

# Install globally for development
uv tool install --editable .
```

### Running the Application
```bash
# Interactive REPL mode (local dev)
uv run python main.py

# Using global install
copert

# One-shot commands
copert chat "your message"
copert version
copert config
```

### Testing and Code Quality
```bash
# Run tests
uv run pytest

# Run specific test file
uv run pytest tests/test_filename.py

# Format code
uv run ruff format .

# Type checking
uv run mypy copert/
```

### Configuration
- Uses `.env.copert` file (not `.env`) to avoid conflicts
- Required variables: `OPENAI_API_KEY`, `LANGSMITH_API_KEY`, `EXA_API_KEY`
- Optional: `OPENAI_MODEL`, `OPENAI_TEMPERATURE`, `OPENAI_MAX_TOKENS`, `MAX_ITERATIONS`
- Settings loaded via Pydantic in [copert/config/settings.py](copert/config/settings.py)

## Architecture

### Core Pattern: LangGraph ReAct Loop

```
User Input → Agent (LLM) → Tool Calls?
                ↓              ↓
            No Tools       Execute Tools
                ↓              ↓
              END      ← Agent Summarizes
```

The agent follows a Reasoning + Acting (ReAct) pattern:
1. User sends message to agent
2. Agent (GPT model) decides whether to use tools or respond
3. If tools needed: execute → return results to agent
4. Agent sees results and either uses more tools or provides final response
5. Loop continues until agent decides no more tools needed

### Key Components

**State Management** ([copert/state/conversation.py](copert/state/conversation.py))
- `AgentState`: TypedDict containing `messages` list
- Messages flow: `HumanMessage → AIMessage (with tool_calls) → ToolMessage → AIMessage (summary)`

**Agent Graph** ([copert/agents/graph.py](copert/agents/graph.py))
- `create_agent_graph()`: Creates compiled LangGraph StateGraph
- `agent_node`: Invokes LLM with bound tools
- `tool_node`: Executes tools (with optional approval via ApprovalManager)
- `should_continue`: Routes to tools or END based on AIMessage.tool_calls

**LLM Client** ([copert/llm/](copert/llm/))
- Wraps OpenAI ChatGPT via LangChain
- System prompts in [copert/llm/prompts.py](copert/llm/prompts.py): `COPERT_SYSTEM_PROMPT`, `GENERAL_PURPOSE_SUBAGENT_PROMPT`, `CODE_WRITER_SUBAGENT_PROMPT`

**CLI Interface** ([copert/cli/](copert/cli/))
- Entry point: [copert/cli/entrypoint.py](copert/cli/entrypoint.py)
- Interactive session: [copert/cli/session.py](copert/cli/session.py)
- Uses `prompt_toolkit` for REPL with history and auto-completion
- Uses `rich` for markdown rendering and formatting

**Approval System** ([copert/utils/approval.py](copert/utils/approval.py))
- `ApprovalManager`: Requests user confirmation for destructive operations
- Intercepts `write_file`, `edit_file`, `multiedit` tool calls
- Shows diff previews before applying changes
- Supports auto-approve mode

## Multi-Agent System

### Main Agent (12 tools)
Full access to all tools including execution (bash) and delegation (task).

### Sub-Agent Delegation via `task` tool

**Delegation Architecture:**
```
Main Agent
  ├─ task() → general-purpose Sub-Agent (read-only: 6 tools)
  │            Tools: read_file, ls, grep, glob, webfetch, websearch
  │            Use: Research, searches, pattern analysis
  │
  └─ task() → code-writer Sub-Agent (write access, no exec: 7 tools)
               Tools: read_file, write_file, edit_file, multiedit, ls, grep, glob
               Use: Multi-file implementation, bulk refactoring
```

**How task delegation works** ([copert/tools/task/delegate.py](copert/tools/task/delegate.py)):
1. Main agent calls `task(description, prompt, subagent_type)`
2. Creates fresh StateGraph with specialized system prompt and tool subset
3. Sub-agent autonomously completes task in isolation (recursion_limit=50)
4. Returns final report to main agent
5. Main agent processes report and continues

**Why use sub-agents:**
- **Context efficiency**: Complex operations don't pollute main conversation
- **Specialization**: Each sub-agent optimized for specific domain
- **Safety**:
  - general-purpose: Read-only, cannot modify files
  - code-writer: Can write but cannot execute bash (prevents destructive commands)
- **Separation of concerns**: Research vs. implementation isolated

**When to delegate:**
- To general-purpose: Multi-file searches, pattern analysis across codebase, documentation research
- To code-writer: Feature implementation spanning multiple files, bulk refactoring
- When NOT to delegate: 1-3 known files, simple single-file edits, tasks requiring test execution

## Tools Architecture

All tools defined in [copert/tools/](copert/tools/) using LangChain `@tool` decorator.

**Tool Categories:**
- **File Operations** ([copert/tools/file_ops/](copert/tools/file_ops/)): read_file, write_file, edit_file, multiedit, ls
- **Search** ([copert/tools/search/](copert/tools/search/)): grep (ripgrep wrapper), glob (pattern matching)
- **Execution** ([copert/tools/execution/bash.py](copert/tools/execution/bash.py)): bash (shell command execution)
- **Task Management** ([copert/tools/task_management/todowrite.py](copert/tools/task_management/todowrite.py)): todowrite (task lists)
- **Web** ([copert/tools/web/](copert/tools/web/)): webfetch (fetch URLs), websearch (Exa API)
- **Delegation** ([copert/tools/task/delegate.py](copert/tools/task/delegate.py)): task (spawn sub-agents)

**Tool Sets** ([copert/tools/__init__.py](copert/tools/__init__.py)):
- `ALL_TOOLS`: Main agent (12 tools)
- `READ_ONLY_TOOLS`: general-purpose sub-agent (6 tools)
- `CODE_WRITER_TOOLS`: code-writer sub-agent (7 tools)

## Important Implementation Details

### Path Handling
- Working directory is where user invoked `copert`
- Always use relative paths for project files (e.g., `src/main.py`, not `/src/main.py`)
- Use `.` for current directory operations
- Absolute paths only when provided by user

### Message Flow in Graph
```python
# Typical flow:
[HumanMessage("write a prime function")]
→ [AIMessage(content="...", tool_calls=[{write_file...}])]  # Agent decides to use tool
→ [ToolMessage(content="File written", name="write_file")]   # Tool executes
→ [AIMessage(content="I created prime.py...")]               # Agent summarizes
```

### Tool Node with Approval
When `ApprovalManager` is provided to `create_agent_graph()`:
- Custom `approval_tool_node` replaces standard `ToolNode`
- Intercepts tool calls before execution
- For destructive ops (write/edit/multiedit): shows preview, requests approval
- Approved: execute tool → return ToolMessage
- Rejected: return ToolMessage with "Operation rejected by user"

### Error Handling in Sub-Agents
- `GraphRecursionError`: Sub-agent exceeded 50 iterations (task too broad)
- `RecursionError`: Python call stack too deep
- Both return helpful error messages to main agent

### Configuration Loading
[copert/config/settings.py](copert/config/settings.py) uses `pydantic-settings`:
- Loads from `.env.copert` file
- Falls back to environment variables
- Exits with helpful message if required keys missing
- Settings instance created at module import time

## Common Patterns

### Adding a New Tool
1. Create tool file in appropriate [copert/tools/](copert/tools/) subdirectory
2. Define with `@tool` decorator and Pydantic `BaseModel` for args
3. Import in [copert/tools/__init__.py](copert/tools/__init__.py)
4. Add to `ALL_TOOLS` list (and `READ_ONLY_TOOLS`/`CODE_WRITER_TOOLS` if applicable)
5. LLM automatically gets access via `bind_tools()` in graph

### Adding a New Sub-Agent Type
1. Create system prompt in [copert/llm/prompts.py](copert/llm/prompts.py)
2. Define tool subset in [copert/tools/__init__.py](copert/tools/__init__.py)
3. Add case in `task()` function in [copert/tools/task/delegate.py](copert/tools/task/delegate.py)
4. Update `valid_types` list

### Modifying Agent Behavior
- Main agent: Edit `COPERT_SYSTEM_PROMPT` in [copert/llm/prompts.py](copert/llm/prompts.py)
- Sub-agents: Edit `GENERAL_PURPOSE_SUBAGENT_PROMPT` or `CODE_WRITER_SUBAGENT_PROMPT`
- Graph logic: Modify [copert/agents/graph.py](copert/agents/graph.py)

## Testing Strategy

Tests located in [tests/](tests/):
- Test individual tools with mocked dependencies
- Test agent graph flow with mock LLM
- Integration tests for CLI commands
- Use `pytest-asyncio` for async tests

## Dependencies

Key dependencies (see [pyproject.toml](pyproject.toml)):
- `langgraph`: Multi-agent state graph orchestration
- `langchain` + `langchain-openai`: LLM and tool abstractions
- `prompt-toolkit`: Interactive REPL
- `rich`: Terminal formatting
- `typer`: CLI framework
- `pydantic`: Settings and data validation
- `exa-py`: Web search API
- External: `ripgrep` (must be installed separately)
