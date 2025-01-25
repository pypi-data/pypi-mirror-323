import click
from ai_kit.utils import print_stream
import importlib.resources
import logging
from rich.console import Console
from pathlib import Path
from ..utils.env import load_environment
from ..config import CoreConfig
import warnings
from ..utils.fs import remove_tree
from ..cli.templating import copy_dir
from .status import status_command
import sys
import os
from rich.table import Table
import asyncio
from .registry import registry_instance

# Load environment variables
load_environment(CoreConfig.ROOT_DIR)

logger = logging.getLogger(__name__)
console_instance = Console()  # ? singleton
error_console_instance = Console(stderr=True)  # ? singleton

registry_instance.set_console_instance(console_instance)

# Filter out warnings from internal dependencies
warnings.filterwarnings("ignore", module="pydantic.*")
warnings.filterwarnings("ignore", module="openai.*")

# ! MAIN COMMAND ===============================================
# This is the entry point for the CLI


@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="ERROR",
    help="Set logging level",
)
def main(ctx, log_level):
    """AI development toolkit for managing prompts and scripts."""

    # Set logging level
    logger.setLevel(log_level.upper())

    # Handle no subcommand
    if ctx.invoked_subcommand is None:
        ctx.invoke(help)


# ! INIT COMMAND ===============================================
# This is the command for initializing the [ROOT_DIR] directory structure
# It copies over the template files and makes the .index dir


@main.command()
@click.option(
    "--force", "-f", is_flag=True, help="Overwrite existing configuration and files"
)
@registry_instance.add(
    name="init",
    description="Initialize a new .ai directory structure.",
    usage="ai-kit init [--force]",
)
def init(force: bool):
    """Initialize a new .ai directory structure."""
    ROOT_DIR = Path(CoreConfig.ROOT_DIR)

    # If force is true and root dir exists, remove it entirely
    if force and ROOT_DIR.exists():
        try:
            remove_tree(ROOT_DIR)
            console_instance.print(
                f"[yellow]Removed existing {ROOT_DIR} directory[/yellow]"
            )
        except Exception as e:
            error_console_instance = Console(stderr=True)
            error_console_instance.print(f"[red]Error removing directory: {e}[/red]")
            sys.exit(1)

    pkg_root = importlib.resources.files(
        "ai_kit"
    )  # points to the actual package installation
    # so we use this for our src dir. ROOT_DIR is the project root dir the user will see

    try:
        # copy files over to root dir
        copy_dir(
            pkg_root / "templates", ROOT_DIR
        )  # thiss will create the dest dir if it doesn't exist
        console_instance.print(
            "[green]✓ Initialized directory structure with templates[/green]"
        )

        # Make the .index dir for storing text files
        os.makedirs(ROOT_DIR / ".index", exist_ok=True)
        console_instance.print("[green]✓ Initialized .index directory[/green]")

        console_instance.print(
            "\n[bold green]✨ AI Kit initialization complete![/bold green]"
        )

    except Exception as e:
        error_console = Console(stderr=True)
        error_console.print(f"[red]Error creating directory structure: {e}[/red]")
        sys.exit(1)


# ! COMMMANDS ===============================================
# These are the rest of the commands
# web, think (deepseek, return <think> only), find, reason, list/help or something


@click.argument("query")
@click.option(
    "--max-results",
    "-n",
    type=int,
    default=10,
    help="Maximum number of results to return",
)
@main.command()
@registry_instance.add(
    name="web",
    description="Search the web for information.",
    usage="ai-kit web <query> [--max-results <n>]",
)
def web(query: str, max_results: int):
    """Search the web for information."""
    from ..cli.web import search_web

    results = search_web(query, max_results)

    # Create and configure the table
    table = Table(show_header=True, header_style="bold magenta", show_lines=True)
    table.add_column("Title", style="cyan", no_wrap=False)
    table.add_column("Link", style="blue")
    table.add_column("Snippet", style="green", no_wrap=False)

    # Add rows to the table
    for result in results:
        table.add_row(
            result.get("title", "N/A"),
            result.get("link", "N/A"),
            result.get("snippet", "N/A"),
        )

    # Print the table
    console_instance.print(table)


@click.argument("prompt")
@click.option(
    "--model", "-m", type=str, default="o1", help="Model to use for reasoning"
)
@main.command()
@registry_instance.add(
    name="reason",
    description="Consult with a smart AI designed to perform reasoning. You can pass {{ filepath }} in the prompt to reference files in the codebase.",
    usage="ai-kit reason <prompt> [--model <model>]",
)
async def reason(prompt: str, model: str):
    """Reason about the prompt."""
    from ..cli.reason import reason_command

    asyncio.run(reason_command(prompt, model))


@click.argument("prompt")
@main.command()
@registry_instance.add(
    name="think",
    description="Access your brain. If the request is complex enough, this will call on a smar AI to generate a thought stream. Otherwise it will return back to you. You can pass {{ filepath }} in the prompt to reference files in the codebase.",
    usage="ai-kit think <prompt>",
)
def think(prompt: str):
    """Think about the prompt."""
    from ..cli.think import think_command
    asyncio.run(think_command(prompt))


@main.command()
@registry_instance.add(
    name="help",
    description="Show help information.",
    usage="ai-kit help",
)
def help():
    """Show help information."""
    console_instance.print("\n[bold cyan]AI Kit - The first CLI designed for AI agents[/bold cyan]\n")
    
    # Show version
    from .. import __version__
    console_instance.print(f"[bold]Version:[/bold] {__version__}\n")
    
    # Show available commands
    console_instance.print("[bold]Available Commands:[/bold]")
    registry_instance.display_commands()
    
    # Show initialization hint
    console_instance.print("\n[bold yellow]Getting Started:[/bold yellow]")
    console_instance.print("1. Initialize AI Kit in your project:")
    console_instance.print("   ai-kit init")
    console_instance.print("\n2. Try the think command:")
    console_instance.print("   ai-kit think \"What files are in this project?\"")
    
    # Show more info
    console_instance.print("\n[bold]For more information:[/bold]")
    console_instance.print("- Use --help with any command for detailed usage")
    console_instance.print("- Visit https://github.com/beneverman/ai-kit for documentation")


@main.command()
@registry_instance.add(
    name="status",
    description="Show status information.",
    usage="ai-kit status",
)
def status():
    """Show status information."""
    status_command(console_instance)


# ! MUST BE THE LAST COMMAND ===============================================
# This is the command for listing all commands so every command is registered

@main.command()
@registry_instance.add(
    name="list",
    description="List all commands.",
    usage="ai-kit list.",
)
def list():
    """List all commands."""
    registry_instance.display_commands()
