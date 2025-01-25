"""Local search index operations."""

import asyncio
from typing import Optional
from rich.console import Console
from ai_kit.config import CoreConfig

console = Console()

async def execute_index(force: bool = False, model: Optional[str] = None) -> None:
    """Execute index command with lazy loading of dependencies."""
    # Only import when needed
    from ai_kit.core.llms.litellm_client import EmbeddingClient
    from ai_kit.core.local.index import LocalSearchIndex
    
    try:
        client = EmbeddingClient(model)
        index = LocalSearchIndex(
            embedding_client=client,
            text_dir=f"{CoreConfig.ROOT_DIR}/local",
            index_path=f"{CoreConfig.ROOT_DIR}/local/faiss.idx",
            mapping_path=f"{CoreConfig.ROOT_DIR}/local/mapping.json",
            embedding_cache_path=f"{CoreConfig.ROOT_DIR}/local/embedding_cache.json",
            bm25_cache_path=f"{CoreConfig.ROOT_DIR}/local/bm25_corpus.json"
        )
        
        await index.build(force=force)
        console.print("[green]✓ Successfully indexed documents[/green]")
            
    except Exception as e:
        console.print(f"[red]Error during indexing: {str(e)}[/red]")

async def execute_status() -> None:
    """Execute status command with lazy loading of dependencies."""
    # Only import when needed
    from ai_kit.core.llms.litellm_client import EmbeddingClient
    from ai_kit.core.local.index import LocalSearchIndex
    
    try:
        client = EmbeddingClient()
        index = LocalSearchIndex(
            embedding_client=client,
            text_dir=f"{CoreConfig.ROOT_DIR}/local",
            index_path=f"{CoreConfig.ROOT_DIR}/local/faiss.idx",
            mapping_path=f"{CoreConfig.ROOT_DIR}/local/mapping.json",
            embedding_cache_path=f"{CoreConfig.ROOT_DIR}/local/embedding_cache.json",
            bm25_cache_path=f"{CoreConfig.ROOT_DIR}/local/bm25_corpus.json"
        )
        
        # Load index and mapping
        index.load_faiss_index()
        index.load_mapping()
        
        # Gather stats
        total_vectors = index.index.ntotal if index.index else 0
        total_files = len(set(m['filename'] for m in index.mapping.values()))
        total_chunks = len(index.mapping)
        
        console.print("\n[bold]Local Search Index Status[/bold]")
        console.print("=======================")
        console.print(f"Total files indexed: {total_files}")
        console.print(f"Total text chunks: {total_chunks}")
        console.print(f"Total vectors: {total_vectors}")
        console.print(f"Index dimension: {index.dimension}")
        console.print(f"\nPaths:")
        console.print(f"  Text directory: {index.text_dir}")
        console.print(f"  FAISS index: {index.index_path}")
        console.print(f"  Mapping file: {index.mapping_path}")
        console.print(f"  Embedding cache: {index.embedding_cache_path}")
        console.print(f"  BM25 cache: {index.bm25_cache_path}")
            
    except Exception as e:
        console.print(f"[red]Error getting status: {str(e)}[/red]")

def index_command(force: bool = False, model: Optional[str] = None) -> None:
    """CLI command for indexing functionality."""
    asyncio.run(execute_index(force, model))

def status_command() -> None:
    """CLI command for status functionality."""
    asyncio.run(execute_status()) 