import asyncio

from ai_kit.core.index import LocalSearchIndex

async def search_command(query: str, max_results: int = 5, debug: bool = False):
    """Search the index for information."""
    index = LocalSearchIndex(debug=debug)
    return await index.search(query, max_results=max_results)
    