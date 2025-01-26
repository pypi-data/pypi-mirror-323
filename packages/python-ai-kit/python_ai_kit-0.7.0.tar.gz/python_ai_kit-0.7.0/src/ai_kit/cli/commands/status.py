from rich.console import Console
from rich.emoji import Emoji
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from dotenv import load_dotenv
from ai_kit.config import CoreConfig, LiteLLMConfig
import os

load_dotenv()

def obscure_key(key: str) -> str:
    if not key:
        return "not set"
    return key[:6] + "..." + key[-4:]

def status_command(console: Console) -> None:
    """Display AI Kit status information."""
    # Create main status table
    table = Table(
        title="🔍 AI Kit Status",
        title_style="bold cyan",
        show_header=False,
        box=None,
        padding=(0, 1)
    )
    table.add_column("Key", style="bold blue")
    table.add_column("Value", style="white")

    # Add system information
    table.add_row(
        "📂 Root Directory",
        Text(str(CoreConfig.ROOT_DIR), style="green")
    )
    
    # Add API keys section
    table.add_row("", "")  # Empty row for spacing
    table.add_row(
        Text("🔑 API Keys", style="bold yellow"),
        ""
    )
    
    for key in LiteLLMConfig.api_keys():
        value = os.getenv(key)
        has_key = value is not None
        status_style = "green" if has_key else "red"
        status_icon = "✓" if has_key else "✗"
        table.add_row(
            f"  {key}",
            Text(
                f"{status_icon} {obscure_key(value) if has_key else 'not set'}", 
                style=status_style
            )
        )

    console.print()
    console.print(table)
    console.print()
