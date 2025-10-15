"""Approval manager for requesting user confirmation before destructive operations."""

from typing import Dict, Any, Optional, Callable
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from prompt_toolkit import PromptSession


class ApprovalManager:
    """Manages user approval for destructive tool operations."""

    def __init__(self, console: Console, prompt_session: PromptSession, auto_approve: bool = False):
        """Initialize the approval manager.

        Args:
            console: Rich console for displaying previews
            prompt_session: PromptSession for interactive approval prompts
            auto_approve: If True, automatically approve all operations
        """
        self.console = console
        self.prompt_session = prompt_session
        self.auto_approve = auto_approve
        self.approval_history = []
        self.status_callback: Optional[Callable[[bool], None]] = None

    def to_code_block(self, text: str, language: str = "python") -> str:
        """Convert text to a markdown code block.

        Args:
            text: Text to convert to a code block
            language: Programming language for syntax highlighting
        """
        return f"```{language}\n{text}\n```"

    def set_status_callback(self, callback: Callable[[bool], None]):
        """Set callback to control status spinner during approval.

        Args:
            callback: Function that takes a boolean (True=start, False=stop)
        """
        self.status_callback = callback

    def set_auto_approve(self, enabled: bool):
        """Enable or disable auto-approve mode.

        Args:
            enabled: True to auto-approve all operations
        """
        self.auto_approve = enabled
        status = "enabled" if enabled else "disabled"
        self.console.print(f"[yellow]Auto-approve mode {status}[/yellow]")

    def request_approval(self, tool_name: str, args: Dict[str, Any]) -> bool:
        """Request user approval for a tool operation.

        Args:
            tool_name: Name of the tool being invoked
            args: Arguments passed to the tool

        Returns:
            True if approved, False if rejected
        """
        # Auto-approve if enabled
        if self.auto_approve:
            return True

        # Only request approval for destructive operations
        if tool_name not in ['write_file', 'edit_file', 'multiedit']:
            return True

        # Show approval prompt based on tool type
        if tool_name == 'write_file':
            return self._approve_write(args)
        elif tool_name == 'edit_file':
            return self._approve_edit(args)
        elif tool_name == 'multiedit':
            return self._approve_multiedit(args)

        return True

    def _approve_write(self, args: Dict[str, Any]) -> bool:
        """Request approval for write_file operation.

        Args:
            args: Tool arguments containing file_path and content

        Returns:
            True if approved, False if rejected
        """
        file_path = args.get('file_path', 'unknown')
        content = args.get('content', '')

        # Show preview
        self.console.print()
        self.console.print(Panel(
            f"[yellow]⚠️  Write File Operation[/yellow]\n\n"
            f"File: [cyan]{file_path}[/cyan]\n"
            f"Action: [bold]Create/Overwrite[/bold]\n"
            f"Size: {len(content)} characters, {content.count(chr(10)) + 1} lines",
            title="Approval Required",
            border_style="yellow"
        ))

        # Show content preview (first 20 lines)
        lines = content.split('\n')
        preview_lines = lines[:20]
        if len(lines) > 20:
            preview_lines.append(f"... ({len(lines) - 20} more lines)")

        # Detect language for syntax highlighting
        language = "python" if file_path.endswith('.py') else "text"
        syntax = Syntax('\n'.join(preview_lines), language, theme="monokai", line_numbers=True)

        self.console.print("\n[bold]Content Preview:[/bold]")
        self.console.print(syntax)
        self.console.print()

        # Stop status spinner if callback is set
        if self.status_callback:
            self.status_callback(False)

        # Request approval using prompt_toolkit
        while True:
            response = self.prompt_session.prompt("📝 Allow this file write? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                approved = True
                break
            elif response in ['n', 'no']:
                approved = False
                break
            else:
                self.console.print("[yellow]Please answer 'y' or 'n'[/yellow]")

        # Restart status spinner if callback is set
        if self.status_callback:
            self.status_callback(True)

        # Track decision
        self.approval_history.append({
            'tool': 'write_file',
            'file': file_path,
            'approved': approved
        })

        return approved

    def _approve_edit(self, args: Dict[str, Any]) -> bool:
        """Request approval for edit_file operation.

        Args:
            args: Tool arguments containing file_path, old_string, new_string

        Returns:
            True if approved, False if rejected
        """
        file_path = args.get('file_path', 'unknown')
        old_string = args.get('old_string', '')
        new_string = args.get('new_string', '')
        replace_all = args.get('replace_all', False)

        # Show preview
        self.console.print()
        self.console.print(Panel(
            f"[yellow]⚠️  Edit File Operation[/yellow]\n\n"
            f"File: [cyan]{file_path}[/cyan]\n"
            f"Action: [bold]{'Replace All' if replace_all else 'Replace Once'}[/bold]",
            title="Approval Required",
            border_style="yellow"
        ))

        # Detect language for syntax highlighting
        language = "python" if file_path.endswith('.py') else ""

        # Show diff
        self.console.print("\n[bold]Changes:[/bold]")
        self.console.print("[red]- Old:[/red]")
        self.console.print(Panel(Markdown(self.to_code_block(old_string, language)), border_style="red"))
        self.console.print("[green]+ New:[/green]")
        self.console.print(Panel(Markdown(self.to_code_block(new_string, language)), border_style="green"))
        self.console.print()

        # Stop status spinner if callback is set
        if self.status_callback:
            self.status_callback(False)

        # Request approval using prompt_toolkit
        while True:
            response = self.prompt_session.prompt("✏️  Allow this file edit? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                approved = True
                break
            elif response in ['n', 'no']:
                approved = False
                break
            else:
                self.console.print("[yellow]Please answer 'y' or 'n'[/yellow]")

        # Restart status spinner if callback is set
        if self.status_callback:
            self.status_callback(True)

        # Track decision
        self.approval_history.append({
            'tool': 'edit_file',
            'file': file_path,
            'approved': approved
        })

        return approved

    def _approve_multiedit(self, args: Dict[str, Any]) -> bool:
        """Request approval for multiedit operation.

        Args:
            args: Tool arguments containing file_path and edits list

        Returns:
            True if approved, False if rejected
        """
        file_path = args.get('file_path', 'unknown')
        edits = args.get('edits', [])

        # Show preview
        self.console.print()
        self.console.print(Panel(
            f"[yellow]⚠️  Multiple Edit Operation[/yellow]\n\n"
            f"File: [cyan]{file_path}[/cyan]\n"
            f"Action: [bold]Apply {len(edits)} edits[/bold]",
            title="Approval Required",
            border_style="yellow"
        ))

        # Detect language for syntax highlighting
        language = "python" if file_path.endswith('.py') else ""

        # Show each edit
        self.console.print("\n[bold]Edits to Apply:[/bold]")
        for i, edit in enumerate(edits, 1):
            self.console.print(f"\n[bold]Edit {i}:[/bold]")
            self.console.print("[red]- Old:[/red]")
            old_str = edit.get('old_string', '')
            truncated_old = old_str[:200] + ("\n..." if len(old_str) > 200 else "")
            self.console.print(Panel(Markdown(self.to_code_block(truncated_old, language)), border_style="red"))
            self.console.print("[green]+ New:[/green]")
            new_str = edit.get('new_string', '')
            truncated_new = new_str[:200] + ("\n..." if len(new_str) > 200 else "")
            self.console.print(Panel(Markdown(self.to_code_block(truncated_new, language)), border_style="green"))

        self.console.print()

        # Stop status spinner if callback is set
        if self.status_callback:
            self.status_callback(False)

        # Request approval using prompt_toolkit
        while True:
            response = self.prompt_session.prompt(f"✏️  Apply all {len(edits)} edits? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                approved = True
                break
            elif response in ['n', 'no']:
                approved = False
                break
            else:
                self.console.print("[yellow]Please answer 'y' or 'n'[/yellow]")

        # Restart status spinner if callback is set
        if self.status_callback:
            self.status_callback(True)

        # Track decision
        self.approval_history.append({
            'tool': 'multiedit',
            'file': file_path,
            'approved': approved,
            'edit_count': len(edits)
        })

        return approved

    def get_approval_stats(self) -> Dict[str, int]:
        """Get statistics about approval decisions.

        Returns:
            Dictionary with approval/rejection counts
        """
        approved = sum(1 for h in self.approval_history if h['approved'])
        rejected = sum(1 for h in self.approval_history if not h['approved'])

        return {
            'approved': approved,
            'rejected': rejected,
            'total': len(self.approval_history)
        }
