from typing import Dict, Any
from ai_kit.cli import console_instance

def search_web(query: str, max_results: int = 10) -> list[Dict[str, Any]]:
    """Search the web for information."""
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        console_instance.print("[red]Error: duckduckgo_search is not installed. Please install it using 'pip install duckduckgo-search'[/red]")
        return []

    with DDGS() as ddgs:
        return ddgs.text(query, max_results=max_results)