"""Interactive REPL session for Copert CLI."""

from typing import List
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, ToolMessage
import langsmith as ls
from copert.config import settings

from copert.agents import create_agent_graph
from copert import __version__

client = ls.Client(
    api_key=settings.langsmith_api_key,  
    api_url="https://api.smith.langchain.com", 
)

class CopertSession:
    """Interactive REPL session for Copert CLI."""

    def __init__(self):
        """Initialize the interactive session."""
        self.console = Console()
        self.history = InMemoryHistory()
        self.session = PromptSession(history=self.history)
        self.messages: List[BaseMessage] = []
        self.graph = None  # Lazy load on first use

        # Custom prompt style
        self.prompt_style = Style.from_dict({
            'prompt': '#00aa00 bold',
        })

    def _get_graph(self):
        """Lazy load the agent graph."""
        if self.graph is None:
            self.graph = create_agent_graph()
        return self.graph

    def display_welcome(self):
        """Display welcome message."""
        welcome_text = f"""
# Welcome to Copert CLI v{__version__}

Your AI coding assistant. Type your message and press Enter to chat.

**Commands:**
- `/help` - Show this help message
- `/clear` - Clear conversation history
- `/list-agents` - List available agents
- `/history` - Show conversation history
- `/exit` or `/quit` - Exit the session
- `Ctrl+D` - Exit the session
- `Ctrl+C` - Cancel current input

Let's get started!
        """
        self.console.print(Panel(Markdown(welcome_text.strip()), border_style="green"))
        self.console.print()

    def display_help(self):
        """Display help message."""
        help_text = """
# Copert CLI Help

**Available Commands:**
- `/help` - Show this help message
- `/clear` - Clear conversation history
- `/history` - Show conversation history
- `/list-agents` - List available agents
- `/exit` or `/quit` - Exit the session

**Keyboard Shortcuts:**
- `Ctrl+D` - Exit
- `Ctrl+C` - Cancel current input
- `↑/↓` - Navigate command history

**Features:**
- Maintains conversation context across turns
- Supports file operations, code search, and bash commands
- Uses GPT-4 with function calling for tool execution
        """
        self.console.print(Markdown(help_text.strip()))
        self.console.print()

    def display_history(self):
        """Display conversation history."""
        if not self.messages:
            self.console.print("[dim]No conversation history yet.[/dim]\n")
            return

        self.console.print("\n[bold]Conversation History:[/bold]\n")
        for i, msg in enumerate(self.messages, 1):
            if isinstance(msg, HumanMessage):
                self.console.print(f"[cyan]{i}. You:[/cyan] {msg.content}")
            elif isinstance(msg, AIMessage):
                content = msg.content if msg.content else "[Tool calls only]"
                self.console.print(f"[green]{i}. Copert:[/green] {content[:500]}...")
        self.console.print()

    def clear_history(self):
        """Clear conversation history."""
        self.messages = []
        self.graph = None  # Reset graph to clear state
        self.console.print("[yellow]Conversation history cleared.[/yellow]\n")

    def list_agents(self):
        """List available agents."""
        self.console.print("[bold]Available Agents:[/bold]")
        self.console.print("general-purpose: Read-only research")
        self.console.print("code-writer: Code implementation")
        self.console.print()

    def handle_command(self, user_input: str) -> bool:
        """Handle special commands.

        Args:
            user_input: User's input string

        Returns:
            True if input was a command and was handled, False otherwise
        """
        command = user_input.strip().lower()

        if command in ["/exit", "/quit"]:
            self.console.print("\n[green]Goodbye! 👋[/green]\n")
            return True

        if command == "/help":
            self.display_help()
            return False

        if command == "/history":
            self.display_history()
            return False

        if command == "/clear":
            self.clear_history()
            return False

        if command == "/list-agents":
            self.list_agents()
            return False

        return False

    def process_message(self, user_input: str):
        """Process a user message and get response from the agent.

        Args:
            user_input: User's message
        """
        with ls.tracing_context(client=client, project_name="copert-cli", enabled=True):
            try:
                # Add user message to history
                self.messages.append(HumanMessage(content=user_input))

                graph = self._get_graph()

                # Show thinking indicator while streaming
                with self.console.status("[bold green]Coperting...\n", spinner="dots") as status:
                    # Stream the graph execution to display tool calls in real-time
                    # Using stream_mode="updates" to get complete messages per node
                    for chunk in graph.stream({"messages": self.messages}, stream_mode="updates"):
                        # chunk is a dict like: {"agent": {"messages": [...]}} or {"tools": {"messages": [...]}}
                        for node_name, node_output in chunk.items():
                            # Extract messages from node output
                            if "messages" in node_output:
                                for message in node_output["messages"]:
                                    # Append each complete message to our history
                                    self.messages.append(message)

                                    # Display tool calls when agent decides to use tools
                                    if isinstance(message, AIMessage) and message.tool_calls:
                                        status.stop()

                                        for tool_call in message.tool_calls:
                                            tool_name = tool_call.get('name', 'unknown')
                                            args = tool_call.get('args', {})

                                            # Special formatting for todowrite tool
                                            if tool_name == 'todowrite' and 'todos' in args:
                                                self.console.print(f"\n[cyan]📋 Task List:[/cyan]\n")
                                                for i, todo in enumerate(args['todos'], 1):
                                                    status_emoji = {
                                                        'pending': '⏳',
                                                        'in_progress': '🔄',
                                                        'completed': '✅'
                                                    }.get(todo.get('status', 'pending'), '⏳')

                                                    content = todo.get('content', 'Unknown task')
                                                    self.console.print(f"   {status_emoji} {i}. {content}")
                                                self.console.print()
                                            # Special formatting for task delegation tool
                                            elif tool_name == 'task' and 'description' in args and 'subagent_type' in args:
                                                description = args.get('description', 'Unknown task')
                                                subagent_type = args.get('subagent_type', 'unknown')
                                                self.console.print(f"\n[cyan]🤖 Delegating to {subagent_type} sub-agent:[/cyan] [bold]{description}[/bold]\n")
                                            else:
                                                # Standard tool call display
                                                self.console.print(f"\n[cyan]🔧 Using tool:[/cyan] [bold]{tool_name}[/bold]")

                                                # Display tool arguments
                                                if args:
                                                    for key, value in args.items():
                                                        # Truncate long values for display
                                                        str_value = str(value)
                                                        if len(str_value) > 100:
                                                            str_value = str_value[:500] + "..."
                                                        self.console.print(f"   [dim]{key}:[/dim] {str_value}")

                                        # Resume status
                                        status.start()

                                    # Display tool completion
                                    elif isinstance(message, ToolMessage):
                                        # Temporarily stop status to print completion
                                        status.stop()

                                        # Check if tool execution was successful
                                        status_icon = "✓"
                                        status_color = "green"

                                        # Tool messages contain the result in content
                                        # If it starts with "Error:", mark as failed
                                        if message.content and message.content.startswith("Error:"):
                                            status_icon = "✗"
                                            status_color = "red"

                                        self.console.print(f"[{status_color}]{status_icon} Tool completed[/{status_color}]\n")

                                        # Resume status
                                        status.start()

                # Get the last AI message (final response)
                last_message = self.messages[-1]

                # Display final response
                self.console.print("[bold green]Copert:[/bold green]")
                if isinstance(last_message, AIMessage) and last_message.content:
                    md = Markdown(last_message.content)
                    self.console.print(md)
                else:
                    self.console.print("[dim]No response generated[/dim]")

                self.console.print()

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Cancelled[/yellow]\n")
            except Exception as e:
                self.console.print(f"\n[bold red]Error:[/bold red] {str(e)}\n")

    def run(self):
        """Run the interactive REPL session."""
        self.display_welcome()

        while True:
            try:
                # Get user input
                user_input = self.session.prompt(
                    "You: ",
                    style=self.prompt_style,
                    multiline=False,
                )

                # Skip empty input
                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    should_exit = self.handle_command(user_input)
                    if should_exit:
                        break
                    continue

                # Process regular message
                self.process_message(user_input)

            except KeyboardInterrupt:
                # Ctrl+C - just show new prompt
                self.console.print()
                continue

            except EOFError:
                # Ctrl+D - exit
                self.console.print("\n[green]Goodbye! 👋[/green]\n")
                break

            except Exception as e:
                self.console.print(f"\n[bold red]Unexpected error:[/bold red] {str(e)}\n")
                continue
