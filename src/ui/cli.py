"""
Rich-based CLI interface for the Writer-Editor review loop system.

This module provides an interactive command-line interface with
beautiful formatting using the Rich library.
"""

from typing import Optional
from uuid import uuid4

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box
from langgraph.types import Command
from langgraph.errors import GraphInterrupt

from src.graph.workflow import compile_workflow, create_initial_state
from src.config.settings import settings


class CLI:
    """
    Command-line interface for Writer-Editor workflow.

    This class provides methods for starting and managing workflow sessions
    with beautiful terminal output using Rich.
    """

    def __init__(self, mode: str = "multi-agent"):
        """
        Initialize the CLI.

        Args:
            mode: Workflow mode ('simple' or 'multi-agent')
        """
        self.console = Console()
        self.mode = mode
        self.app = compile_workflow(mode)

    def print_banner(self):
        """Display welcome banner."""
        banner_text = """
# Writer-Editor Review Loop System

**Mode**: {mode}
**LLM**: {model} @ {url}

Ready to create high-quality content!
        """.format(
            mode=self.mode.upper(),
            model=settings.lm_studio_model,
            url=settings.lm_studio_base_url
        )

        self.console.print(Panel(
            Markdown(banner_text),
            border_style="blue",
            box=box.DOUBLE
        ))

    def start_session(
        self,
        topic: Optional[str] = None,
        thread_id: Optional[str] = None,
        max_iterations: Optional[int] = None,
        max_outline_revisions: Optional[int] = None
    ):
        """
        Start a new workflow session or resume an existing one.

        Args:
            topic: Content topic (prompts if None)
            thread_id: Session ID for resumption (creates new if None)
            max_iterations: Override default max iterations
            max_outline_revisions: Override default max outline revisions
        """
        self.print_banner()

        # Get topic if not provided
        if not topic:
            topic = Prompt.ask("\n[bold cyan]What topic would you like to write about?[/bold cyan]")

        # Generate or use provided thread_id
        if not thread_id:
            thread_id = str(uuid4())
            self.console.print(f"\n[dim]Session ID: {thread_id}[/dim]")

        # Create initial state
        initial_state = create_initial_state(
            topic=topic,
            mode=self.mode,
            max_iterations=max_iterations,
            max_outline_revisions=max_outline_revisions
        )

        # Create config with thread_id
        config = {"configurable": {"thread_id": thread_id}}

        self.console.print(f"\n[bold green]Starting workflow for topic:[/bold green] {topic}\n")

        try:
            # Stream workflow events
            for event in self.app.stream(initial_state, config, stream_mode="values"):
                self._handle_event(event)

            self.console.print("\n[bold green]✓ Workflow completed successfully![/bold green]")

        except GraphInterrupt as gi:
            # Handle user intervention
            self._handle_interrupt(gi, config, thread_id)

        except Exception as e:
            self.console.print(f"\n[bold red]✗ Error:[/bold red] {e}")
            raise

    def _handle_event(self, event: dict):
        """
        Handle workflow event and display to user.

        Args:
            event: Event dictionary from workflow stream
        """
        stage = event.get("current_stage", "")

        if stage == "intent_analysis_complete":
            self._display_intent_analysis(event)
        elif stage == "outline_created":
            self._display_outline(event)
        elif stage == "outline_reviewed":
            self._display_outline_review(event)
        elif stage == "research_complete":
            self._display_research_summary(event)
        elif stage == "draft_created":
            self._display_draft(event)
        elif stage == "draft_reviewed":
            self._display_feedback(event)

    def _handle_interrupt(self, interrupt_event: GraphInterrupt, config: dict, thread_id: str):
        """
        Handle user intervention interrupt.

        Args:
            interrupt_event: The GraphInterrupt exception
            config: Workflow configuration
            thread_id: Session thread ID
        """
        # Get user input
        stage = interrupt_event.args[0] if interrupt_event.args else "unknown"

        if "outline" in stage.lower():
            user_input = self._get_outline_decision()
        else:
            user_input = self._get_draft_decision()

        # Resume workflow with user input
        try:
            for event in self.app.stream(Command(resume=user_input), config, stream_mode="values"):
                self._handle_event(event)

            self.console.print("\n[bold green]✓ Workflow completed![/bold green]")

        except GraphInterrupt as gi:
            # Another intervention point
            self._handle_interrupt(gi, config, thread_id)

        except Exception as e:
            self.console.print(f"\n[bold red]✗ Error:[/bold red] {e}")
            raise

    def _display_intent_analysis(self, event: dict):
        """Display user intent analysis."""
        intent = event.get("user_intent")
        if not intent:
            return

        self.console.print(Panel(
            f"""[bold]Document Type:[/bold] {intent['document_type']}
[bold]Target Audience:[/bold] {intent['target_audience']}
[bold]Tone:[/bold] {intent['tone']}
[bold]Objectives:[/bold] {', '.join(intent['objectives'])}""",
            title="[bold cyan]Intent Analysis[/bold cyan]",
            border_style="cyan"
        ))

    def _display_outline(self, event: dict):
        """Display content outline."""
        outline = event.get("current_outline")
        if not outline:
            return

        sections_text = ""
        for idx, section in enumerate(outline["sections"], 1):
            sections_text += f"\n{idx}. [bold]{section['title']}[/bold]\n"
            sections_text += f"   {section['purpose']}\n"

        self.console.print(Panel(
            f"""[bold]Structure:[/bold] {outline['overall_structure']}
[bold]Estimated Length:[/bold] {outline['estimated_total_length']}

[bold]Sections:[/bold]{sections_text}""",
            title=f"[bold cyan]Outline v{outline['version']}[/bold cyan]",
            border_style="cyan"
        ))

    def _display_outline_review(self, event: dict):
        """Display outline review."""
        review = event.get("current_outline_review")
        if not review:
            return

        status = "✓ APPROVED" if review["approved"] else "✗ NEEDS REVISION"
        style = "green" if review["approved"] else "yellow"

        strengths = "\n".join(f"  • {s}" for s in review["strengths"])
        weaknesses = "\n".join(f"  • {w}" for w in review["weaknesses"]) if review["weaknesses"] else "None"

        self.console.print(Panel(
            f"""[bold {style}]{status}[/bold {style}]

[bold]Strengths:[/bold]
{strengths}

[bold]Areas for Improvement:[/bold]
{weaknesses}

[bold]Assessment:[/bold]
{review['overall_assessment']}""",
            title="[bold magenta]Outline Review[/bold magenta]",
            border_style="magenta"
        ))

    def _display_research_summary(self, event: dict):
        """Display research summary."""
        research_by_section = event.get("research_by_section", {})
        if not research_by_section:
            self.console.print("[dim]No research performed[/dim]")
            return

        total_sources = sum(len(r["sources"]) for r in research_by_section.values())

        self.console.print(Panel(
            f"""[bold]Sections Researched:[/bold] {len(research_by_section)}
[bold]Total Sources:[/bold] {total_sources}

Research data ready for writing.""",
            title="[bold green]Research Complete[/bold green]",
            border_style="green"
        ))

    def _display_draft(self, event: dict):
        """Display draft content."""
        draft = event.get("current_draft", "")
        iteration = event.get("iteration_count", 0)

        # Show preview (first 500 chars)
        preview = draft[:500] + "..." if len(draft) > 500 else draft

        self.console.print(Panel(
            preview,
            title=f"[bold blue]Draft (Iteration {iteration})[/bold blue]",
            border_style="blue"
        ))

        self.console.print(f"[dim]Full length: {len(draft)} characters[/dim]\n")

    def _display_feedback(self, event: dict):
        """Display editor feedback."""
        feedback = event.get("current_feedback", "")

        self.console.print(Panel(
            feedback,
            title="[bold yellow]Editor Feedback[/bold yellow]",
            border_style="yellow"
        ))

    def _get_outline_decision(self) -> str:
        """
        Get user decision on outline.

        Returns:
            User decision: 'proceed' or 'revise'
        """
        self.console.print("\n[bold]Outline Decision[/bold]")

        choices = ["proceed", "revise"]
        decision = Prompt.ask(
            "What would you like to do?",
            choices=choices,
            default="proceed"
        )

        return decision

    def _get_draft_decision(self) -> str:
        """
        Get user decision on draft.

        Returns:
            User decision: 'continue' or 'stop'
        """
        self.console.print("\n[bold]Draft Decision[/bold]")

        choices = ["continue", "stop"]
        decision = Prompt.ask(
            "What would you like to do?",
            choices=choices,
            default="stop"
        )

        return decision

    def display_session_history(self, thread_id: str):
        """
        Display history of a session.

        Args:
            thread_id: Session ID to display
        """
        # This would query the checkpoint database
        # Implementation depends on checkpoint structure
        self.console.print(f"[dim]Session history for: {thread_id}[/dim]")
        self.console.print("[yellow]History display not yet implemented[/yellow]")

    def list_sessions(self):
        """List all available sessions."""
        # This would query the checkpoint database
        self.console.print("[yellow]Session listing not yet implemented[/yellow]")
