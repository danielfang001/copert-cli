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
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=4096
MAX_ITERATIONS=25
```

**Note:** Copert uses `.env.copert` instead of `.env` to avoid conflicts with your project's environment variables.

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

## Development

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format .

# Type check
uv run mypy copert/
```

## License

None
