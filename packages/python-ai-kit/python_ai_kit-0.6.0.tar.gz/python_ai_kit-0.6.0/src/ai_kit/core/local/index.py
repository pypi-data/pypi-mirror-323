import os
import json
import hashlib
import asyncio
import time
from typing import List, Dict, Any, Optional

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from ai_kit.core.llms.litellm_client import EmbeddingClient
import logging
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from ai_kit.config import CoreConfig

logger = logging.getLogger(__name__)
console = Console()

# ---------------------------------------------------------------------------------
# Utility function: chunk text by paragraph, then chunk again if paragraphs are large
# ---------------------------------------------------------------------------------
def paragraph_chunk(
    text: str,
    max_char_length: int = 1000
) -> List[str]:
    """
    Split text into paragraphs by double newlines, then
    further chunk any paragraph larger than `max_char_length`.
    Returns a list of chunk strings.
    """
    start_time = time.perf_counter()
    raw_paragraphs = text.split("\n\n")
    chunks = []

    for paragraph in raw_paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        # If paragraph is short enough, keep it
        if len(paragraph) <= max_char_length:
            chunks.append(paragraph)
        else:
            # Further chunk the large paragraph in max_char_length pieces
            start = 0
            while start < len(paragraph):
                end = start + max_char_length
                sub_chunk = paragraph[start:end]
                chunks.append(sub_chunk)
                start = end


    duration = time.perf_counter() - start_time
    logger.debug(f"Chunked text into {len(chunks)} chunks (took {duration:.3f}s)")
    return chunks


# ---------------------------------------------------------------------------------
# Main Class: LocalSearchIndex
#   - Stores chunk snippets
#   - Uses paragraph chunking
#   - Hybrid search (BM25 + FAISS)
#   - Caching embeddings in JSON
# ---------------------------------------------------------------------------------
class LocalSearchIndex:
    def __init__(
        self,
        embedding_client: EmbeddingClient,
        text_dir: str = f"{CoreConfig.ROOT_DIR}/local/",
        index_path: str = f"{CoreConfig.ROOT_DIR}/local/faiss.idx",
        mapping_path: str = f"{CoreConfig.ROOT_DIR}/local/mapping.json",
        embedding_cache_path: str = f"{CoreConfig.ROOT_DIR}/local/embedding_cache.json",
        bm25_cache_path: str = ".ai/local/bm25_corpus.json",
        max_paragraph_size: int = 1000
    ):
        """
        Args:
            embedding_client (get_embedding_client): The async embedding client.
            text_dir (str): Directory with .txt files.
            index_path (str): Path to the FAISS index file.
            mapping_path (str): Path to the JSON file that maps chunk_ids -> metadata.
            embedding_cache_path (str): Path to JSON file caching md5(chunk_text) -> embedding vector.
            bm25_cache_path (str): (Optional) Where we store tokenized corpus for BM25 for quick load.
            max_paragraph_size (int): Max characters before chunking paragraphs further.
        """
        logger.info("Initializing LocalSearchIndex")
        logger.debug(f"Using text directory: {text_dir}")
        logger.debug(f"Using index path: {index_path}")
        logger.debug(f"Using mapping path: {mapping_path}")
        logger.debug(f"Using embedding cache path: {embedding_cache_path}")
        logger.debug(f"Using BM25 cache path: {bm25_cache_path}")
        logger.debug(f"Max paragraph size: {max_paragraph_size}")

        self.client = embedding_client  # your provided client
        self.text_dir = Path(text_dir)
        self.index_path = Path(index_path)
        self.mapping_path = Path(mapping_path)
        self.embedding_cache_path = Path(embedding_cache_path)
        self.bm25_cache_path = Path(bm25_cache_path)
        self.supported_extensions = {".txt", ".md"}

        # Dimension inferred from the client
        self.dimension = self.client.dimension
        logger.debug(f"Using embedding dimension: {self.dimension}")

        # For chunking
        self.max_paragraph_size = max_paragraph_size

        # FAISS Index object
        self.index = None

        # chunk_id -> { filename, chunk_text, md5, ... }
        self.mapping: Dict[str, Any] = {}

        # embedding_cache: md5_of_text -> List[float]
        self.embedding_cache: Dict[str, List[float]] = {}

        # For BM25
        # We'll store a list of tokenized chunks in memory, plus
        # a separate ID-to-chunk mapping so we know which is which.
        self.bm25_corpus: List[List[str]] = []
        self.bm25 = None  # BM25Okapi object

        # Load existing data if available
        self.load_faiss_index()
        self.load_mapping()
        self.load_embedding_cache()
        self.load_bm25_cache()

    # ---------------------------------------------------------
    # Basic disk I/O
    # ---------------------------------------------------------
    def load_faiss_index(self) -> None:
        start_time = time.perf_counter()
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(str(self.index_path))
            # dimension from the index
            self.dimension = self.index.d
            duration = time.perf_counter() - start_time
            logger.info(f"Loaded existing index (dim={self.dimension})")
            logger.debug(f"Loading FAISS index took {duration:.3f}s")
        else:
            logger.info("No index found; creating a new one")
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            self.index.hnsw.efConstruction = 40
            self.index.hnsw.efSearch = 16
            duration = time.perf_counter() - start_time
            logger.debug(f"Creating new FAISS index took {duration:.3f}s")

    def save_faiss_index(self) -> None:
        if self.index is not None:
            start_time = time.perf_counter()
            faiss.write_index(self.index, str(self.index_path))
            duration = time.perf_counter() - start_time
            logger.info(f"Saved index to {self.index_path}")
            logger.debug(f"Saving FAISS index took {duration:.3f}s")

    def load_mapping(self) -> None:
        start_time = time.perf_counter()
        if os.path.exists(self.mapping_path):
            with open(self.mapping_path, "r", encoding="utf-8") as f:
                self.mapping = json.load(f)
            duration = time.perf_counter() - start_time
            logger.debug(f"Loaded mapping with {len(self.mapping)} entries (took {duration:.3f}s)")
        else:
            self.mapping = {}
            logger.debug("No mapping file found, starting fresh")

    def save_mapping(self) -> None:
        start_time = time.perf_counter()
        with open(self.mapping_path, "w", encoding="utf-8") as f:
            json.dump(self.mapping, f, indent=2)
        duration = time.perf_counter() - start_time
        logger.info(f"Saved mapping to {self.mapping_path}")
        logger.debug(f"Saving mapping took {duration:.3f}s")

    def load_embedding_cache(self) -> None:
        start_time = time.perf_counter()
        if os.path.exists(self.embedding_cache_path):
            with open(self.embedding_cache_path, "r", encoding="utf-8") as f:
                self.embedding_cache = json.load(f)
            duration = time.perf_counter() - start_time
            logger.debug(f"Loaded embedding cache with {len(self.embedding_cache)} entries (took {duration:.3f}s)")
        else:
            self.embedding_cache = {}
            logger.debug("No embedding cache found, starting fresh")

    def save_embedding_cache(self) -> None:
        start_time = time.perf_counter()
        with open(self.embedding_cache_path, "w", encoding="utf-8") as f:
            json.dump(self.embedding_cache, f, indent=2)
        duration = time.perf_counter() - start_time
        logger.info(f"Saved embedding cache to {self.embedding_cache_path}")
        logger.debug(f"Saving embedding cache took {duration:.3f}s")

    def load_bm25_cache(self) -> None:
        start_time = time.perf_counter()
        if os.path.exists(self.bm25_cache_path):
            with open(self.bm25_cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # data is { chunk_id -> token_list }
            chunk_ids = sorted(list(data.keys()), key=lambda x: int(x))
            self.bm25_corpus = [data[cid] for cid in chunk_ids]
            self.bm25 = BM25Okapi(self.bm25_corpus)
            duration = time.perf_counter() - start_time
            logger.info("Loaded BM25 corpus from disk")
            logger.debug(f"Loading BM25 corpus took {duration:.3f}s")
        else:
            self.bm25_corpus = []
            self.bm25 = None
            logger.debug("No BM25 cache found, starting fresh")

    def save_bm25_cache(self) -> None:
        if not self.bm25_corpus:
            return
        start_time = time.perf_counter()
        # We must match ordering of self.mapping's chunk_ids
        # We'll build a dict chunk_id->token_list
        data = {}
        # We assume bm25_corpus[i] corresponds to chunk_id=i if built in that order
        # We'll track that in a controlled manner when building the corpus.
        for chunk_id_str, meta in self.mapping.items():
            i = int(chunk_id_str)
            # If i is in range of bm25_corpus, store it
            if 0 <= i < len(self.bm25_corpus):
                data[chunk_id_str] = self.bm25_corpus[i]
        with open(self.bm25_cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        duration = time.perf_counter() - start_time
        logger.info(f"Saved BM25 corpus to {self.bm25_cache_path}")
        logger.debug(f"Saving BM25 corpus took {duration:.3f}s")

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------
    def compute_md5(self, file_path: str) -> str:
        start_time = time.perf_counter()
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        result = hasher.hexdigest()
        duration = time.perf_counter() - start_time
        logger.debug(f"Computing MD5 for {file_path} took {duration:.3f}s")
        return result
    
    def crawl_dir(self) -> List[tuple[str, str]]:
        """
        Crawl the directory and find all supported files.
        
        Returns:
            List of tuples (absolute_path, relative_path) for each supported file
        """
        start_time = time.perf_counter()
        paths = []
        dir_path = os.path.abspath(self.text_dir)
        
        for root, _, files in os.walk(dir_path):
            for file in files:
                if any(file.endswith(ext) for ext in self.supported_extensions):
                    abs_path = os.path.join(root, file)
                    # Get path relative to the text directory
                    rel_path = os.path.relpath(abs_path, dir_path)
                    paths.append((abs_path, rel_path))
        
        duration = time.perf_counter() - start_time
        logger.debug(f"Crawling directory took {duration:.3f}s, found {len(paths)} files")
        return paths

    async def get_embedding(self, text: str) -> np.ndarray:
        """
        Get the embedding for a single chunk of text, using cache if available.
        Returns a 1D numpy array (float32).
        """
        start_time = time.perf_counter()
        
        # Cache key: MD5 of the text itself
        text_md5 = hashlib.md5(text.encode("utf-8")).hexdigest()
        if text_md5 in self.embedding_cache:
            embedding_list = self.embedding_cache[text_md5]
            duration = time.perf_counter() - start_time
            logger.debug(f"Retrieved embedding from cache (took {duration:.3f}s)")
        else:
            cache_check_duration = time.perf_counter() - start_time
            logger.debug(f"Cache miss (check took {cache_check_duration:.3f}s)")
            
            embed_start = time.perf_counter()
            embedding_list = await self.client.embed(text)
            embed_duration = time.perf_counter() - embed_start
            logger.debug(f"Computing embedding took {embed_duration:.3f}s")
            
            # Save to cache
            cache_start = time.perf_counter()
            self.embedding_cache[text_md5] = embedding_list
            cache_duration = time.perf_counter() - cache_start
            logger.debug(f"Saving to cache took {cache_duration:.3f}s")

        # Convert to float32 numpy array
        convert_start = time.perf_counter()
        result = np.array(embedding_list, dtype=np.float32)
        convert_duration = time.perf_counter() - convert_start
        logger.debug(f"Converting to numpy took {convert_duration:.3f}s")
        
        total_duration = time.perf_counter() - start_time
        logger.debug(f"Total get_embedding took {total_duration:.3f}s")
        return result

    # ---------------------------------------------------------
    # Indexing (with chunking & caching)
    # ---------------------------------------------------------
    async def reindex_texts(self, force_reindex: bool = False):
        """
        Index or re-index the text files in self.text_dir, using paragraph chunking.
        Also builds a BM25 corpus in parallel.
        """
        start_time = time.perf_counter()
        timings = {}
        
        # Load all caches
        t0 = time.perf_counter()
        self.load_faiss_index()
        self.load_mapping()
        self.load_embedding_cache()
        self.load_bm25_cache()
        timings["Loading Caches"] = time.perf_counter() - t0

        # Find all supported files with their relative paths
        t0 = time.perf_counter()
        files = self.crawl_dir()
        timings["Directory Scan"] = time.perf_counter() - t0
        logger.info(f"Found {len(files)} supported files in {self.text_dir}")

        # If no files found, initialize empty state and return
        if not files:
            logger.warning("No supported files found to index")
            # Initialize empty FAISS index if needed
            if self.index is None:
                self.index = faiss.IndexHNSWFlat(self.dimension, 32)
                self.index.hnsw.efConstruction = 40
                self.index.hnsw.efSearch = 16
            # Initialize empty BM25
            self.bm25_corpus = []
            self.bm25 = BM25Okapi([["dummy"]])  # Initialize with dummy doc to prevent div by 0
            # Save empty state
            self.save_faiss_index()
            self.save_mapping()
            self.save_embedding_cache()
            self.save_bm25_cache()
            return

        t0 = time.perf_counter()
        total_chunks = 0
        for abs_path, rel_path in files:
            file_md5 = self.compute_md5(abs_path)

            # If not force_reindex, skip if MD5 unchanged
            file_needs_update = True
            if not force_reindex:
                for _, meta in self.mapping.items():
                    if meta["rel_path"] == rel_path and meta["md5"] == file_md5:
                        file_needs_update = False
                        break

            if file_needs_update:
                logger.info(f"Processing file: {rel_path}")
                with open(abs_path, "r", encoding="utf-8") as fobj:
                    text_data = fobj.read()

                chunks = paragraph_chunk(text_data, max_char_length=self.max_paragraph_size)
                total_chunks += len(chunks)

                # If the index is brand new or dimension mismatch, recreate:
                if self.index.ntotal == 0 and self.index.d != self.dimension:
                    self.index = faiss.IndexHNSWFlat(self.dimension, 32)
                    self.index.hnsw.efConstruction = 40
                    self.index.hnsw.efSearch = 16
                    logger.info(f"Re-created index with dimension {self.dimension}")

                for chunk_id, chunk_text in enumerate(chunks):
                    # Create a new vector ID
                    new_id = self.index.ntotal

                    # Get or compute embedding
                    embedding = await self.get_embedding(chunk_text)
                    embedding_2d = embedding[np.newaxis, :]  # shape (1, d)

                    # Add to FAISS index
                    self.index.add(embedding_2d)

                    # Prepare lexical tokens for BM25
                    tokenized_chunk = chunk_text.split()
                    while len(self.bm25_corpus) <= new_id:
                        self.bm25_corpus.append([])
                    self.bm25_corpus[new_id] = tokenized_chunk

                    # Update mapping with chunk metadata
                    self.mapping[str(new_id)] = {
                        "filename": os.path.basename(abs_path),
                        "rel_path": rel_path,
                        "md5": file_md5,
                        "chunk_text": chunk_text
                    }
        timings["Processing Files"] = time.perf_counter() - t0

        # Build a fresh BM25 index from self.bm25_corpus
        t0 = time.perf_counter()
        self.bm25 = BM25Okapi(self.bm25_corpus)
        timings["Building BM25"] = time.perf_counter() - t0

        # Save all data
        t0 = time.perf_counter()
        self.save_faiss_index()
        self.save_mapping()
        self.save_embedding_cache()
        self.save_bm25_cache()
        timings["Saving Data"] = time.perf_counter() - t0

        total_time = time.perf_counter() - start_time
        
        # Display performance metrics with rich styling
        if logger.getEffectiveLevel() <= logging.INFO:
            table = Table(title="Indexing Performance")
            table.add_column("Operation", style="cyan")
            table.add_column("Duration", style="magenta")
            table.add_column("Percentage", style="green")
            
            for step, duration in timings.items():
                percentage = (duration / total_time) * 100
                table.add_row(
                    step,
                    f"{duration:.3f}s",
                    f"{percentage:.1f}%"
                )
            
            table.add_row(
                "Total",
                f"{total_time:.3f}s",
                "100%",
                style="bold"
            )
            
            console.print()
            console.print(Panel(table, expand=False))
            console.print(f"[green]✓ Indexed {len(files)} files with {total_chunks} chunks[/green]")
            console.print()

    # ---------------------------------------------------------
    # Hybrid Search
    # ---------------------------------------------------------
    async def search(self, query: str, top_k: int = 5):
        """
        Hybrid search combining FAISS and BM25 results.
        """
        start_time = time.perf_counter()
        timings = {}
        
        # Load all necessary data
        t0 = time.perf_counter()
        if not os.path.exists(self.index_path) or not os.path.exists(self.mapping_path):
            logger.warning("No index or mapping found. Run reindex_texts first.")
            return []

        if self.index is None:
            self.load_faiss_index()

        if not self.mapping:
            self.load_mapping()

        if not self.embedding_cache:
            self.load_embedding_cache()

        if self.bm25 is None:
            self.load_bm25_cache()
            if self.bm25 is None:
                logger.debug("Building BM25 from mapping")
                if not self.mapping:
                    logger.warning("No documents indexed yet")
                    return []
                    
                tokenized_corpus = []
                max_id = 0
                for chunk_id_str, meta in self.mapping.items():
                    cid = int(chunk_id_str)
                    max_id = max(max_id, cid)
                tokenized_corpus = [[] for _ in range(max_id + 1)]
                for chunk_id_str, meta in self.mapping.items():
                    cid = int(chunk_id_str)
                    tokenized_corpus[cid] = meta["chunk_text"].split()
                if not tokenized_corpus:
                    tokenized_corpus = [["dummy"]]  # Prevent div by 0
                self.bm25 = BM25Okapi(tokenized_corpus)
                self.bm25_corpus = tokenized_corpus
        timings["Loading Data"] = time.perf_counter() - t0

        if not self.mapping:
            logger.warning("No documents indexed yet")
            return []

        # Embedding-based search (FAISS)
        t0 = time.perf_counter()
        query_emb = await self.get_embedding(query)
        query_emb_2d = query_emb[np.newaxis, :]
        distances, ids = self.index.search(query_emb_2d, top_k)
        
        embedding_results = []
        for dist, idx in zip(distances[0], ids[0]):
            if idx == -1:
                continue
            inv_dist_score = 1.0 / (1.0 + dist)
            embedding_results.append((idx, inv_dist_score))
        timings["FAISS Search"] = time.perf_counter() - t0

        # BM25 search
        t0 = time.perf_counter()
        tokenized_query = query.split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_top_indices = np.argsort(bm25_scores)[::-1][:top_k]
        bm25_results = [(int(i), bm25_scores[i]) for i in bm25_top_indices]
        timings["BM25 Search"] = time.perf_counter() - t0

        # Combine results
        t0 = time.perf_counter()
        scale_factor = 15.0
        combined_scores = {}

        for (cid, emb_score) in embedding_results:
            combined_scores[cid] = combined_scores.get(cid, 0.0) + emb_score

        for (cid, bm_score) in bm25_results:
            combined_scores[cid] = combined_scores.get(cid, 0.0) + (bm_score / scale_factor)

        sorted_combined = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        results = []
        for cid, score in sorted_combined:
            meta = self.mapping.get(str(cid), {})
            results.append({
                "chunk_id": cid,
                "filename": meta.get("filename", "unknown"),
                "chunk_text": meta.get("chunk_text", ""),
                "score": score,
                "rel_path": meta.get("rel_path", "unknown")
            })
        timings["Result Processing"] = time.perf_counter() - t0
        
        total_time = time.perf_counter() - start_time

        # Display performance metrics only if log level is INFO or DEBUG
        if logger.getEffectiveLevel() <= logging.INFO:
            # Performance table
            perf_table = Table(title="Search Performance")
            perf_table.add_column("Operation", style="cyan")
            perf_table.add_column("Duration", style="magenta")
            perf_table.add_column("Percentage", style="green")
            
            for step, duration in timings.items():
                percentage = (duration / total_time) * 100
                perf_table.add_row(
                    step,
                    f"{duration:.3f}s",
                    f"{percentage:.1f}%"
                )
            
            perf_table.add_row(
                "Total",
                f"{total_time:.3f}s",
                "100%",
                style="bold"
            )
            
            console.print()
            console.print(Panel(perf_table, expand=False))
            console.print()

        # Always display results with rich markdown
        if results:
            console.print(f"[green]✓ Found {len(results)} results for query:[/green] [cyan]{query}[/cyan]")
            console.print()

            for i, result in enumerate(results, 1):
                # Create a markdown string with the result info
                md_content = f"""
### Result {i} - {result['rel_path']} (Score: {result['score']:.3f})

{result['chunk_text']}
"""
                console.print(Panel(
                    Markdown(md_content),
                    title=f"[cyan]Result {i}[/cyan]",
                    border_style="blue"
                ))
                console.print()
        else:
            console.print("[yellow]No results found[/yellow]")
            console.print()

        return results


# ---------------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------------
# If you want to test quickly from a script, you can do something like:
if __name__ == "__main__":
    # Usage example (requires an event loop)
    async def main():
        # Create your custom embedding client
        embedding_client = EmbeddingClient("text-embedding-3-small")

        # Initialize the local search index 
        search_index = LocalSearchIndex(
            embedding_client=embedding_client,
            text_dir=f"{CoreConfig.ROOT_DIR}/local",
            index_path=f"{CoreConfig.ROOT_DIR}/local/faiss.idx",
            mapping_path=f"{CoreConfig.ROOT_DIR}/local/mapping.json",
            embedding_cache_path=f"{CoreConfig.ROOT_DIR}/local/embedding_cache.json",
            bm25_cache_path=f"{CoreConfig.ROOT_DIR}/local/bm25_corpus.json",
            max_paragraph_size=1000
        )

        # Reindex
        await search_index.reindex_texts(force_reindex=False)

        # Query
        query_str = "example query about neural networks"
        results = await search_index.search(query_str, top_k=5)
        print("Hybrid search results:")
        for r in results:
            print(r)

    asyncio.run(main())