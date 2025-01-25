"""Search command implementation."""

import click
import asyncio
from typing import Optional
from rich.console import Console

console = Console()

async def execute_search(query: str, max_results: Optional[int] = None) -> None:
    """Execute search command with lazy loading of dependencies."""
    # Only import embedding client when needed
    from ..llms.litellm_client import get_embedding_client
    from ..local.index import LocalSearchIndex
    
    try:
        # Initialize clients and index
        embedding_client = get_embedding_client()
        index = LocalSearchIndex(embedding_client)
        
        # Perform search
        results = await index.search(query, top_k=max_results or 10)
        
        # Display results
        for result in results:
            console.print(f"[bold]{result.get('rel_path', 'Unknown')}[/bold]")
            console.print(result.get('chunk_text', ''))
            console.print("---")
            
    except Exception as e:
        console.print(f"[red]Error during search: {str(e)}[/red]")

def search_command(query: str, max_results: Optional[int] = None) -> None:
    """CLI command for search functionality."""
    asyncio.run(execute_search(query, max_results)) 