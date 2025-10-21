# Copert CLI

**Co**de Ex**pert** - An AI coding assistant CLI built with LangGraph and OpenAI, adapted from Claude Code.

## Overview

Copert is a command-line coding assistant that helps you with software engineering tasks including writing code, debugging, refactoring, searching codebases, and more. Built on LangGraph for multi-agent orchestration and powered by OpenAI's GPT models.

## Features

- **Interactive REPL**: Continuous conversation with context preservation
- **File Operations**: Read, write, and edit files
- **Code Search**: Search for patterns using ripgrep and glob
- **Command Execution**: Run bash commands and scripts
- **ReAct Pattern**: Reasoning + Acting agent loop for complex tasks
- **Tool Calling**: Native OpenAI function calling with LangChain tools
- **Command History**: Navigate previous commands with arrow keys

## Installation

### Prerequisites

Copert requires ripgrep for code search functionality:

```bash
# macOS
brew install ripgrep

# Linux
apt install ripgrep    # Debian/Ubuntu
yum install ripgrep    # RedHat/CentOS

# Windows
choco install ripgrep
```

### Global Installation (Recommended)

Install Copert CLI globally to use from any directory:

```bash
# Clone the repository
git clone git@github.com:danielfang001/copert-cli.git
cd copert-cli

# Install globally with uv tool
uv tool install --editable .

# Update shell PATH (one-time setup)
uv tool update-shell

# Restart your shell or run:
export PATH="$HOME/.local/bin:$PATH"
```

Now you can use `copert` from anywhere!

### Local Development Installation

```bash
# Clone the repository
git clone git@github.com:danielfang001/copert-cli.git
cd copert-cli

# Install dependencies with uv
uv sync
```

## Configuration

Create a `.env.copert` file in your project directory (or working directory where you invoke copert):

```env
OPENAI_API_KEY=your_key_here
LANGSMITH_API_KEY=your_langsmith_key
EXA_API_KEY=your_exa_key
OPENAI_MODEL=gpt-4.1 # recommend using gpt-5 if you have are verified for api streaming
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=4096
MAX_ITERATIONS=25
```

**Note:** Copert uses `.env.copert` instead of `.env` to avoid conflicts with your project's environment variables.

## Project Memory (COPERT.md) (You know where this is from)

Copert supports project-specific context files similar to Claude Code's CLAUDE.md feature. When you have a `COPERT.md` file in your project directory, Copert automatically loads it into the session context to provide better, project-aware assistance.

### Creating COPERT.md

Use the `/init` command to automatically generate a COPERT.md file:

```bash
$ copert
You: /init
```

The init command spawns a specialized sub-agent that:
1. Reads your README.md and dependency files (pyproject.toml, package.json, etc.)
2. Analyzes your project architecture
3. Creates a comprehensive COPERT.md file with:
   - Common development commands (build, test, lint)
   - High-level architecture and patterns
   - Important implementation details

### How It Works

- **Automatic Loading**: COPERT.md is automatically loaded when you start a Copert session
- **Context Efficiency**: Offloads token-heavy project context from conversation history
- **Better Assistance**: Copert uses this context to provide more accurate, project-specific help

### When to Use

- First time setting up Copert in a new project
- After major architectural changes
- To help Copert understand your project's conventions and patterns

## Usage

### Interactive Mode (Default)

Start an interactive session by running without arguments:

```bash
$ copert

Welcome to Copert CLI v0.1.0
Type /help for commands, /exit to quit

You: Can you help me write a prime number function?

🔧 Using tool: write_file
   file_path: prime.py
✓ Tool completed

Copert: I've created a prime number function for you in prime.py...

You: Now add unit tests

🔧 Using tool: write_file
   file_path: test_prime.py
✓ Tool completed

Copert: I've added unit tests in test_prime.py...

You: /exit
Goodbye!
```

**Session Commands:**
- `/help` - Show help message
- `/init` - Initialize project with COPERT.md guide file
- `/clear` - Clear conversation history
- `/history` - Show conversation history
- `/exit` or `/quit` - Exit session
- `Ctrl+D` - Exit session
- `Ctrl+C` - Cancel current input
- `↑/↓` - Navigate command history

### One-Shot Mode (For Scripts)

Use specific commands for scripting:

```bash
# One-time chat
copert chat "Read the README file"

# Display version
copert version

# Show configuration
copert config
```

### Local Development Mode

If running from source without global installation:

```bash
# Interactive mode
uv run python main.py

# One-shot commands
uv run python main.py version
```

## Architecture

```
User Message
     ↓
   Agent (LLM with tools)
     ↓
Has tool calls?
├─ Yes → Tools → Agent (summarizes) → End
└─ No → End
```

### Components

- **LangGraph StateGraph**: Manages agent workflow and state
- **LangChain Tools**: File ops, search, execution tools
- **ChatOpenAI**: OpenAI LLM with function calling
- **Prompt Toolkit**: Interactive REPL with history and auto-completion
- **Typer CLI**: Command-line interface for one-shot commands
- **Rich**: Terminal formatting and markdown rendering

## Project Structure

```
copert-cli/
├── copert/
│   ├── agents/         # LangGraph agent and graph
│   ├── cli/            # Typer CLI interface
│   ├── config/         # Settings and schemas
│   ├── llm/            # LangChain ChatOpenAI wrapper
│   ├── state/          # State management
│   ├── tools/          # All tools
│   │   ├── file_ops/   # Read, Write, Edit
│   │   ├── search/     # Grep, Glob
│   │   └── execution/  # Bash
│   └── utils/          # Utilities
├── main.py             # Entry point
└── pyproject.toml      # Dependencies
```

## Tools Available

### File Operations
1. **read_file**: Read files with line numbers
2. **write_file**: Write content to files
3. **edit_file**: Exact string replacement in files
4. **ls**: List directory contents
5. **multiedit**: Make multiple edits to a single file

### Search Tools
6. **grep**: Ripgrep-based code search
7. **glob**: File pattern matching

### Execution
8. **bash**: Execute shell commands

### Task Management
9. **todowrite**: Create and manage task lists

### Web Tools
10. **webfetch**: Fetch and process web content
11. **websearch**: Search the web using Exa API

### Sub-Agent Delegation
12. **task**: Delegate complex tasks to specialized sub-agents

## Sub-Agent System

Copert implements a multi-agent architecture where the main agent can delegate complex, multi-step tasks to specialized sub-agents. This keeps the main conversation focused while allowing thorough, autonomous research in isolated contexts.

### How It Works

```python
# Main agent recognizes complex task and delegates:
task(
    description="Search API endpoints",
    prompt="""
    Search the entire codebase for all API endpoint definitions.
    Look for FastAPI, Flask, and Django patterns.
    Return a structured report organized by file.
    """,
    subagent_type="general-purpose"
)
```

**Flow:**
1. Main agent identifies a complex, multi-step task
2. Spawns a specialized sub-agent with fresh context
3. Sub-agent autonomously completes the task with read-only tools
4. Sub-agent returns comprehensive final report
5. Main agent processes report and continues

### Available Sub-Agent Types

#### general-purpose
Research and analysis specialist for:
- Complex codebase searches (multiple grep/glob operations)
- Multi-file pattern analysis
- Documentation research (webfetch/websearch)
- Exhaustive file exploration

**Tools:** read_file, ls, grep, glob, webfetch, websearch (read-only)

#### code-writer
Code implementation specialist for:
- Implementing features across multiple files
- Bulk refactoring operations
- Applying fixes/patterns to many files
- Code generation with specific requirements

**Tools:** read_file, write_file, edit_file, multiedit, ls, grep, glob (write access, no execution)

### Benefits

- **Context Efficiency**: Complex operations don't pollute main conversation context
- **Specialization**: Each sub-agent has optimized prompts and tool access for their domain
- **Safety**:
  - general-purpose: Read-only, cannot make changes
  - code-writer: Can write but cannot execute (no bash), preventing destructive commands
- **Separation of Concerns**: Research and implementation are isolated processes
- **Parallel Execution**: Can delegate to multiple sub-agents simultaneously
- **Focus**: Main agent stays focused on high-level planning and orchestration
- **Scalability**: Easy to add more specialized sub-agent types

### When Sub-Agents Are Used

The main agent automatically delegates to sub-agents when:

**To general-purpose:**
- Task requires multiple search/grep rounds across many files
- Extensive file exploration without knowing exact locations
- Pattern analysis across the entire codebase
- Research requiring multiple web searches and documentation fetches

**To code-writer:**
- Implementing features that span multiple files
- Bulk refactoring operations (e.g., "refactor all error handling to use ErrorService")
- Applying fixes or patterns to many files
- Code generation with specific structural requirements

### Architecture

```
Main Agent (12 tools)
├─ Full access: read, write, edit, ls, multiedit, grep, glob, bash, todowrite, webfetch, websearch, task
│
├─ Delegates research via 'task' tool
│  ↓
│  general-purpose Sub-Agent (6 read-only tools)
│  ├─ read_file, ls, grep, glob, webfetch, websearch
│  └─ Returns: Research report
│
├─ Delegates implementation via 'task' tool
│  ↓
│  code-writer Sub-Agent (7 write tools, no execution)
│  ├─ read_file, write_file, edit_file, multiedit, ls, grep, glob
│  └─ Returns: Implementation report
│
└─ Processes reports and responds to user
```

### Typical Workflow Example

```
User: "Refactor all database queries to use async/await"

Main Agent:
1. 🤖 Delegates to general-purpose:
   "Search for all sync database query patterns"
   → Report: 15 files with sync queries found

2. 🤖 Delegates to code-writer:
   "Refactor these 15 files to async/await,
    following the pattern in examples/async-query.ts"
   → Report: 15 files updated with changes listed

3. 📝 Main agent summarizes to user and suggests running tests
```

## Development

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format .

# Type check
uv run mypy copert/
```

## Notes

Learned a lot from the context engineering talk from langchain and manus.

## License

None
