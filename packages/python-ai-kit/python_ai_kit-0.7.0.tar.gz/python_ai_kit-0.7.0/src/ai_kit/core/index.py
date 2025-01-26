import os
import json
import hashlib
import asyncio
import time

import faiss
import numpy as np
from rank_bm25 import BM25Okapi

import logging
from pathlib import Path
from rich.console import Console
from rich.table import Table
from time import perf_counter

from ai_kit.core.llms.litellm_client import EmbeddingClient
from ai_kit.config import CoreConfig
from ai_kit.utils import count_tokens, truncate_to_tokens
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Tuple
import logging
import hashlib
from datetime import datetime
import chardet
import threading
from fnmatch import fnmatch

logger = logging.getLogger(__name__)
console = Console()

MAX_TOKENS_PER_REQUEST = 8191


# ---------------------------------------------------------------------------------
# Utility function: chunk text by paragraphs, then further chunk if paragraphs are large
# ---------------------------------------------------------------------------------
def paragraph_chunk(text: str, max_char_length: int = 1000) -> List[str]:
    """
    Split text into paragraphs by double newlines, then
    further chunk any paragraph larger than `max_char_length`.
    Returns a list of chunk strings.
    """
    # If performance is a concern, remove or reduce instrumentation in production:
    # start_time = time.perf_counter()

    raw_paragraphs = text.split("\n\n")
    chunks = []

    for paragraph in raw_paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) <= max_char_length:
            chunks.append(paragraph)
        else:
            start = 0
            while start < len(paragraph):
                end = start + max_char_length
                sub_chunk = paragraph[start:end]
                chunks.append(sub_chunk)
                start = end

    # duration = time.perf_counter() - start_time
    # logger.debug(f"Chunked text into {len(chunks)} chunks (took {duration:.3f}s)")
    return chunks


# ---------------------------------------------------------
# Directory scanning
# ---------------------------------------------------------
def crawl_dir(dir_path: str, supported_extensions: List[str]) -> List[Tuple[str, str]]:
    """
    Crawl self.text_dir for all supported file types.
    Returns list of (absolute_path, relative_path).
    """
    paths = []
    dir_path = os.path.abspath(dir_path)
    for root, _, files in os.walk(dir_path):
        for file in files:
            if any(file.endswith(ext) for ext in supported_extensions):
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, dir_path)
                paths.append((abs_path, rel_path))
    return paths


# ---------------------------------------------------------------------------------
# Main Class: LocalSearchIndex
# ---------------------------------------------------------------------------------
class LocalSearchIndex:
    def __init__(
        self,
        max_paragraph_size: int = 1000,
        model: str = "text-embedding-3-small",
    ):
        """
        Initialize the search index.

        Args:
            max_paragraph_size: Max characters before chunking paragraphs further.
            model: The embedding model to use.
            debug: Whether to enable debug logging and extra performance timing.
        """
        # Minimal instrumentation if not in debug

        logger.info("Initializing LocalSearchIndex")

        self.client = EmbeddingClient(model)  # the embedding client
        self.dimension = self.client.dimension
        self.max_paragraph_size = max_paragraph_size

        # Paths
        self.text_dir = Path(f"{CoreConfig.ROOT_DIR}/{CoreConfig.INDEX_DIR}")
        self.index_path = Path(
            f"{CoreConfig.ROOT_DIR}/{CoreConfig.INDEX_CACHE_DIR}/faiss.idx"
        )
        self.mapping_path = Path(
            f"{CoreConfig.ROOT_DIR}/{CoreConfig.INDEX_CACHE_DIR}/mapping.json"
        )
        self.embedding_cache_path = Path(
            f"{CoreConfig.ROOT_DIR}/{CoreConfig.INDEX_CACHE_DIR}/embedding_cache.json"
        )
        self.bm25_cache_path = Path(
            f"{CoreConfig.ROOT_DIR}/{CoreConfig.INDEX_CACHE_DIR}/bm25_corpus.json"
        )
        self.supported_extensions = CoreConfig.SUPPORTED_FILE_EXTENSIONS

        # Internal data
        self.index = None  # FAISS Index object
        self.mapping: Dict[str, Any] = {}
        self.embedding_cache: Dict[str, List[float]] = {}
        self.bm25_corpus: List[List[str]] = []
        self.bm25 = None

        # Create directories
        os.makedirs(self.text_dir, exist_ok=True)
        os.makedirs(self.index_path.parent, exist_ok=True)

        # Load all existing data once
        s = perf_counter()
        with console.status("[green]Loading data...[/green]") as status:
            self._load_all()
            duration = perf_counter() - s
            status.update(f"[green]Loaded in {duration:.2f}s[/green]")

    # ---------------------------------------------------------
    # Loading/Saving: Only once in init unless forced manually
    # ---------------------------------------------------------
    def _load_all(self) -> None:
        """Load index, mapping, embedding cache, BM25 from disk (if present)."""
        t0 = time.perf_counter()

        self._load_faiss_index()
        self._load_mapping()
        self._load_embedding_cache()
        self._load_bm25_cache()

        elapsed = time.perf_counter() - t0
        logger.debug(f"Completed all loads in {elapsed:2f}s")

    def _save_all(self) -> None:
        """Save index, mapping, embedding cache, BM25 to disk."""
        t0 = time.perf_counter()

        self._save_faiss_index()
        self._save_mapping()
        self._save_embedding_cache()
        self._save_bm25_cache()

        elapsed = time.perf_counter() - t0
        logger.debug(f"Completed all saves in {elapsed:.2f}s")

    # ---------------------------------------------------------
    # Disk I/O: faiss index, mapping, embedding cache, BM25
    # ---------------------------------------------------------
    def _load_faiss_index(self) -> None:
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(str(self.index_path), faiss.IO_FLAG_MMAP)
            self.dimension = self.index.d
            logger.info(f"Loaded existing FAISS index (dim={self.dimension})")
        else:
            logger.info("No index found; creating a new one")
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            self.index.hnsw.efConstruction = 40
            self.index.hnsw.efSearch = 16

    def _save_faiss_index(self) -> None:
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
            logger.info(f"Saved index to {self.index_path}")

    def _load_mapping(self) -> None:
        if os.path.exists(self.mapping_path):
            with open(self.mapping_path, "r", encoding="utf-8") as f:
                self.mapping = json.load(f)
            logger.debug(f"Loaded mapping with {len(self.mapping)} entries")
        else:
            logger.debug("No mapping file found, starting fresh")
            self.mapping = {}

    def _save_mapping(self) -> None:
        with open(self.mapping_path, "w", encoding="utf-8") as f:
            json.dump(self.mapping, f, indent=2)
        logger.info(f"Saved mapping to {self.mapping_path}")

    def _load_embedding_cache(self) -> None:
        if os.path.exists(self.embedding_cache_path):
            with open(self.embedding_cache_path, "r", encoding="utf-8") as f:
                self.embedding_cache = json.load(f)
            logger.debug(
                f"Loaded embedding cache with {len(self.embedding_cache)} entries"
            )
        else:
            logger.debug("No embedding cache found, starting fresh")
            self.embedding_cache = {}

    def _save_embedding_cache(self) -> None:
        with open(self.embedding_cache_path, "w", encoding="utf-8") as f:
            json.dump(self.embedding_cache, f, indent=2)
        logger.info(f"Saved embedding cache to {self.embedding_cache_path}")

    def _load_bm25_cache(self) -> None:
        if os.path.exists(self.bm25_cache_path):
            with open(self.bm25_cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            chunk_ids = sorted(list(data.keys()), key=lambda x: int(x))
            self.bm25_corpus = [data[cid] for cid in chunk_ids]
            self.bm25 = BM25Okapi(self.bm25_corpus)
            logger.info("Loaded BM25 corpus from disk")
        else:
            self.bm25_corpus = []
            self.bm25 = None
            logger.debug("No BM25 cache found, starting fresh")

    def _save_bm25_cache(self) -> None:
        if not self.bm25_corpus:
            return
        data = {}
        for chunk_id_str, meta in self.mapping.items():
            i = int(chunk_id_str)
            if 0 <= i < len(self.bm25_corpus):
                data[chunk_id_str] = self.bm25_corpus[i]
        with open(self.bm25_cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved BM25 corpus to {self.bm25_cache_path}")

    # ---------------------------------------------------------
    # MD5 utility
    # ---------------------------------------------------------
    def compute_md5(self, file_path: str) -> str:
        """Compute MD5 hash of file contents."""
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    # ---------------------------------------------------------
    # Single-chunk embedding (used by 'search')
    # ---------------------------------------------------------
    async def get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for a single chunk of text, using cache if available.
        Returns a 1D numpy array (float32).
        """
        text_md5 = hashlib.md5(text.encode("utf-8")).hexdigest()
        if text_md5 in self.embedding_cache:
            emb_list = self.embedding_cache[text_md5]
        else:
            # Compute fresh
            emb_list: List[List[float]] = await self.client.create_embeddings(text)
            self.embedding_cache[text_md5] = emb_list

        return np.array(emb_list[0], dtype=np.float32)

    # ---------------------------------------------------------
    # Batch embeddings with sub-batching
    # ---------------------------------------------------------
    async def embed_sub_batch(
        self, texts: List[str], batch_index: int
    ) -> List[List[float]]:
        start = time.perf_counter()
        embeddings = await self.client.create_embeddings(texts)
        duration = time.perf_counter() - start
        logger.debug(
            f"Sub-batch {batch_index} returned in {duration:.2f}s ({len(texts)} chunks)"
        )
        return embeddings

    async def get_embeddings_for_list(self, texts: List[str]) -> List[np.ndarray]:
        """
        Given a list of chunk texts, return a list of embeddings (numpy float32).
        Batches them so each request stays within 8191 tokens,
        sending them in parallel via asyncio.gather.
        """
        if not texts:
            return []

        overall_start = time.perf_counter()

        text_md5_list = [hashlib.md5(t.encode("utf-8")).hexdigest() for t in texts]
        results = [None] * len(texts)
        uncached_indices = []
        uncached_texts = []

        # Identify which text is uncached
        for i, md5 in enumerate(text_md5_list):
            if md5 in self.embedding_cache:
                results[i] = np.array(self.embedding_cache[md5][0], dtype=np.float32)
            else:
                uncached_indices.append(i)
                uncached_texts.append(texts[i])

        if not uncached_texts:
            # Everything was cached
            logger.debug("All chunk embeddings were cached.")
            return results

        # Sub-batching by token limit
        sub_batches = []
        sub_batch_maps = []
        current_texts = []
        current_map = []
        current_token_count = 0

        for idx_in_list, text_str in enumerate(uncached_texts):
            tok_count = count_tokens(text_str, encoding_name="cl100k_base")
            if tok_count > MAX_TOKENS_PER_REQUEST:
                # Skip overly large chunk
                logger.debug(f"Skipping chunk with {tok_count} tokens (too large).")
                # produce a zero embedding or handle as you wish
                real_idx = uncached_indices[idx_in_list]
                results[real_idx] = np.zeros(self.dimension, dtype=np.float32)
                continue

            if current_token_count + tok_count <= MAX_TOKENS_PER_REQUEST:
                current_texts.append(text_str)
                current_map.append(idx_in_list)
                current_token_count += tok_count
            else:
                sub_batches.append(current_texts)
                sub_batch_maps.append(current_map)
                current_texts = [text_str]
                current_map = [idx_in_list]
                current_token_count = tok_count

        # Last batch
        if current_texts:
            sub_batches.append(current_texts)
            sub_batch_maps.append(current_map)

        tasks = []
        for i, sb in enumerate(sub_batches):
            tasks.append(self.embed_sub_batch(sb, i))
        sub_batch_results = await asyncio.gather(*tasks)

        # Place results back
        for batch_emb_list, batch_map in zip(sub_batch_results, sub_batch_maps):
            for emb_list, idx_in_subbatch in zip(batch_emb_list, batch_map):
                real_idx = uncached_indices[idx_in_subbatch]
                md5 = text_md5_list[real_idx]
                self.embedding_cache[md5] = [emb_list]
                results[real_idx] = np.array(emb_list, dtype=np.float32)

        elapsed = time.perf_counter() - overall_start
        logger.debug(
            f"Batched embedding for {len(uncached_texts)} new chunks took {elapsed:.2f}s "
            f"({len(sub_batches)} sub-batches)."
        )
        return results

    # ---------------------------------------------------------
    # Check if we need reindex
    # ---------------------------------------------------------
    def needs_reindex(self) -> bool:
        """
        Check if index needs to be updated by comparing file MD5s.
        True if:
          - no index or no mapping
          - files added/removed
          - MD5 mismatch between current files and what's in mapping
        """
        if not os.path.exists(self.index_path) or not os.path.exists(self.mapping_path):
            logger.info("No index or mapping found, reindex needed.")
            return True

        current_files = crawl_dir(self.text_dir, self.supported_extensions)
        if not current_files and not self.mapping:
            logger.info("No files to index and no mapping; nothing to do.")
            return False
        elif not current_files and self.mapping:
            logger.info(
                "Index is not empty but directory is empty — potential removal case."
            )
            # In your original code, you don't handle removal fully. Return True if desired:
            return False  # or True, depending on how you'd like to handle it

        # Build a quick lookup: rel_path -> md5 from disk
        current_md5s = {
            rel_path: self.compute_md5(abs_path) for abs_path, rel_path in current_files
        }

        # Build a quick set of files from mapping
        indexed_md5s = {}
        for cid_str, meta in self.mapping.items():
            rp = meta.get("rel_path")
            fmd5 = meta.get("md5")
            # We only need one chunk's MD5 per file to guess if the entire file changed
            if rp not in indexed_md5s:
                indexed_md5s[rp] = fmd5

        # If file sets differ
        if set(current_md5s.keys()) != set(indexed_md5s.keys()):
            logger.info("File added/removed, reindex needed.")
            return True

        # If any single file's MD5 differs
        for rp, md5 in current_md5s.items():
            if indexed_md5s.get(rp) != md5:
                logger.info(f"File changed: {rp}, reindex needed.")
                return True

        logger.info("No reindex needed - files unchanged.")
        return False

    # ---------------------------------------------------------
    # Reindex (add new or changed files)
    # ---------------------------------------------------------
    async def reindex_texts(self, force_reindex: bool = False):
        """
        Index or re-index text files in self.text_dir, chunk by paragraph.
        Uses sub-batching + asyncio.gather to keep each request under 8191 tokens.
        """
        if not force_reindex and not self.needs_reindex():
            logger.info("No changes detected, skipping reindex.")
            return

        console.print("[green]Reindexing text files...[/green]")
        overall_t0 = time.perf_counter()

        # 1) Optionally reload from disk if you want to ensure you have the latest
        # But since we did so in __init__, you can skip it or do a forced load:
        # self._load_all()  # If you suspect data changed outside of Python process

        # 2) Find files
        files = crawl_dir(self.text_dir, self.supported_extensions)
        if not files:
            logger.warning("No supported files found to index.")
            # Create minimal empty index if truly none
            if self.index is None:
                self.index = faiss.IndexHNSWFlat(self.dimension, 32)
                self.index.hnsw.efConstruction = 40
                self.index.hnsw.efSearch = 16
            # Minimal BM25
            self.bm25_corpus = []
            self.bm25 = BM25Okapi([["dummy"]])
            self._save_all()
            return

        # 3) Collect new or changed chunks
        all_new_chunk_texts = []
        all_new_chunk_metas = []
        updating_files = []

        for abs_path, rel_path in files:
            file_md5 = self.compute_md5(abs_path)
            file_already_indexed = False

            # If not forcing reindex, check if we have a chunk from this file & matching MD5
            if not force_reindex:
                # Quick check: if rel_path -> md5 matches
                # We only need to find *one* chunk that has the matching MD5 for this file
                for cid_str, meta in self.mapping.items():
                    if meta["rel_path"] == rel_path and meta["md5"] == file_md5:
                        file_already_indexed = True
                        break

            if not file_already_indexed:
                updating_files.append(rel_path)
                with open(abs_path, "r", encoding="utf-8") as fobj:
                    text_data = fobj.read()
                chunks = paragraph_chunk(
                    text_data, max_char_length=self.max_paragraph_size
                )

                for chunk_text in chunks:
                    all_new_chunk_texts.append(chunk_text)
                    all_new_chunk_metas.append(
                        {
                            "filename": os.path.basename(abs_path),
                            "rel_path": rel_path,
                            "md5": file_md5,
                            "chunk_text": chunk_text,
                        }
                    )

        if not updating_files:
            console.print("[yellow]No new or changed files to index.[/yellow]")
            return

        console.print(f"[cyan]Updating files: {updating_files}[/cyan]")

        # 4) Embed all new chunks
        new_embeddings = await self.get_embeddings_for_list(all_new_chunk_texts)

        # 5) Add to FAISS & BM25
        for idx, embedding in enumerate(new_embeddings):
            if embedding is None:
                # Possibly chunk was too large or skipped
                continue
            embedding_2d = embedding[np.newaxis, :]
            new_id = self.index.ntotal
            self.index.add(embedding_2d)

            chunk_text = all_new_chunk_metas[idx]["chunk_text"]
            tokenized_chunk = chunk_text.split()
            while len(self.bm25_corpus) <= new_id:
                self.bm25_corpus.append([])
            self.bm25_corpus[new_id] = tokenized_chunk

            # Update mapping
            self.mapping[str(new_id)] = all_new_chunk_metas[idx]

        # 6) (Re)build BM25. If the corpus is large, you might want a more incremental approach
        self.bm25 = BM25Okapi(self.bm25_corpus)

        # 7) Save all
        self._save_all()

        # 8) Timing
        elapsed = time.perf_counter() - overall_t0
        console.print(
            f"[green]✓ Indexed {len(updating_files)} files "
            f"with {len(all_new_chunk_texts)} new chunks in {elapsed:.2f}s[/green]"
        )

    # ---------------------------------------------------------
    # Hybrid Search
    # ---------------------------------------------------------
    async def search(
        self, query: str, max_results: int = 5, silent: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining FAISS (embedding similarity) + BM25 results.
        """
        s = perf_counter()
        with console.status("[green]Searching...[/green]") as status:
            if not self.mapping:
                if not silent:
                    console.print("[yellow]No documents indexed yet[/yellow]")
                return []

            # Optionally reindex if needed
            if self.needs_reindex():
                if not silent:
                    console.print("[yellow]Changes detected, reindexing...[/yellow]")
                await self.reindex_texts()

            # 1) FAISS embedding search
            query_emb = await self.get_embedding(query)
            query_emb_2d = query_emb[np.newaxis, :]
            distances, ids = self.index.search(query_emb_2d, max_results)

            embedding_results = []
            for dist, idx in zip(distances[0], ids[0]):
                if idx == -1:
                    continue
                # Example scoring: inversely related to distance
                score = 1.0 / (1.0 + dist)
                embedding_results.append((idx, score))

            # 2) BM25 search
            if not self.bm25:
                # Fallback if no BM25
                logger.warning("BM25 not built. Returning FAISS results only.")
                combined_results = embedding_results
            else:
                tokenized_query = query.split()
                bm25_scores = self.bm25.get_scores(tokenized_query)
                top_indices = np.argsort(bm25_scores)[::-1][:max_results]
                bm25_results = [(int(i), bm25_scores[i]) for i in top_indices]

                # 3) Combine
                # A simple approach is to sum normalized scores:
                scale_factor = 15.0  # tune if desired
                combined_scores = {}

                for cid, emb_score in embedding_results:
                    combined_scores[cid] = combined_scores.get(cid, 0.0) + emb_score
                for cid, bm_score in bm25_results:
                    combined_scores[cid] = combined_scores.get(cid, 0.0) + (
                        bm_score / scale_factor
                    )

                combined_results = sorted(
                    combined_scores.items(), key=lambda x: x[1], reverse=True
                )[:max_results]

            # Format final
            results = []
            for cid, score in combined_results:
                meta = self.mapping.get(str(cid), {})
                results.append(
                    {
                        "chunk_id": cid,
                        "filename": meta.get("filename", "unknown"),
                        "chunk_text": meta.get("chunk_text", ""),
                        "score": score,
                        "rel_path": meta.get("rel_path", "unknown"),
                    }
                )

        duration = perf_counter() - s

        # Display
        if not silent:
            if results:
                console.print(
                    f"\n[bold cyan]Search results for:[/bold cyan] [yellow]{query}[/yellow]"
                )
                console.print(f"[yellow]Search completed in {duration:.2f}s[/yellow]")
                console.print(
                    f"[dim]Showing top {len(results)} in combined ranking[/dim]\n"
                )
                table = Table(
                    show_header=True, header_style="bold magenta", show_lines=True
                )
                table.add_column("File", style="cyan", no_wrap=True)
                table.add_column("Score", style="green", justify="right", width=10)
                table.add_column("Snippet", style="white")
                for r in results:
                    table.add_row(
                        r["rel_path"],
                        f"{r['score']:.3f}",
                        r["chunk_text"][:200] + "...",
                    )
                console.print(table)
                console.print()
            else:
                console.print("[yellow]No results found[/yellow]\n")

        return results

    async def get_rag_context(
        self, query: str, max_chunks: int = 15, max_tokens: int = 30000
    ) -> str:
        """
        Retrieve relevant context for RAG-based generation.
        Returns a markdown-formatted string containing the most relevant chunks up to max_tokens.

        Args:
            query: The search query
            max_chunks: Maximum number of chunks to retrieve
            max_tokens: Maximum total tokens to include in the context

        Returns:
            A markdown-formatted string containing the context
        """
        # Get search results silently
        results = await self.search(query, max_results=max_chunks, silent=True)
        if not results:
            return "No relevant documents found."

        # Format chunks with metadata
        context_chunks = []
        total_tokens = 0

        for result in results:
            # Format this chunk's content
            chunk_text = (
                f"## {result['rel_path']} (score: {result['score']:.3f})\n\n"
                f"{result['chunk_text']}\n"
            )

            # Check if adding this chunk would exceed token limit
            chunk_tokens = count_tokens(chunk_text)
            if total_tokens + chunk_tokens > max_tokens:
                # If this is the first chunk, truncate it
                if not context_chunks:
                    truncated = truncate_to_tokens(chunk_text, max_tokens)
                    context_chunks.append(truncated)
                break

            # Add chunk and update token count
            context_chunks.append(chunk_text)
            total_tokens += chunk_tokens

        return "\n".join(context_chunks)

class QuickSearchIndex:
    def __init__(
        self,
        text_dir: str,
        supported_extensions: List[str],
        case_sensitive: bool = False,
        keyword_limit: int = 100,  # Increased default for full-text processing
        stopwords: Optional[Set[str]] = None,
        max_file_size: int = 10*1024*1024,  # 10MB safety limit
    ):
        if not os.path.isdir(text_dir):
            raise ValueError(f"Directory {text_dir} does not exist")
        if not supported_extensions:
            raise ValueError("At least one supported extension must be provided")

        self.text_dir = text_dir
        self.supported_extensions = [ext.lower() for ext in supported_extensions]
        self.case_sensitive = case_sensitive
        self.keyword_limit = keyword_limit
        self.stopwords = stopwords or set()
        self.max_file_size = max_file_size
        self.lock = threading.RLock()
        self._index_cache = None
        self._index_timestamp = None
        self._inverted_index = None

    def _get_files(self) -> List[tuple]:
        """Get list of files with size checking"""
        files = []
        for root, _, filenames in os.walk(self.text_dir):
            for fn in filenames:
                if any(fnmatch(fn.lower(), pat) for pat in self.supported_extensions):
                    abs_path = os.path.join(root, fn)
                    rel_path = os.path.relpath(abs_path, self.text_dir)
                    try:
                        size = os.path.getsize(abs_path)
                        if size > self.max_file_size:
                            logger.warning(f"Skipping large file {rel_path} ({size} bytes)")
                            continue
                        mtime = os.path.getmtime(abs_path)
                        files.append((abs_path, rel_path, mtime, size))
                    except OSError as e:
                        logger.warning(f"Could not access {abs_path}: {str(e)}")
        return files

    def _safe_read(self, file_path: str) -> str:
        """Read entire file content with safety checks"""
        try:
            with open(file_path, 'rb') as f:
                if os.path.getsize(file_path) > self.max_file_size:
                    return ""
                
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'
                
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                return f.read()
        except (IOError, UnicodeDecodeError) as e:
            logger.error(f"Error reading {file_path}: {str(e)}")
            return ""

    def _process_keywords(self, text: str) -> Set[str]:
        """Extract and normalize keywords from full text"""
        words = re.findall(r'\w+', text)
        processed = set()
        
        for word in words:
            if not self.case_sensitive:
                word = word.lower()
            if (len(word) > 3 and 
                word not in self.stopwords and 
                not word.isdigit()):
                processed.add(word)
                if len(processed) >= self.keyword_limit:
                    break
        return processed

    def _generate_index(self) -> Dict[str, Dict[str, Any]]:
        """Generate the file index with full-text keywords"""
        with self.lock:
            current_files = self._get_files()
            current_hash = hashlib.md5(str([f[1:] for f in current_files]).encode()).hexdigest()
            
            if self._index_cache and self._index_hash == current_hash:
                return self._index_cache
                
            index = {}
            inverted = {}
            
            for abs_path, rel_path, mtime, size in current_files:
                content = self._safe_read(abs_path)
                
                # Extract keywords from path and full content
                path_keywords = re.findall(r'\w+', rel_path.replace('.', ' '))
                content_keywords = self._process_keywords(content)
                keywords = set(path_keywords).union(content_keywords)
                
                # Update inverted index
                for kw in keywords:
                    inverted.setdefault(kw, []).append(rel_path)
                
                index[rel_path] = {
                    'keywords': list(keywords),
                    'path': rel_path,
                    'mtime': mtime,
                    'size': size,
                    'content_hash': hashlib.md5(content.encode()).hexdigest()
                }
            
            self._index_cache = index
            self._inverted_index = inverted
            self._index_hash = current_hash
            self._index_timestamp = datetime.now()
            
            return index

    @property
    def index(self) -> Dict[str, Dict[str, Any]]:
        """Get current index with caching"""
        return self._generate_index()

    @property
    def inverted_index(self) -> Dict[str, List[str]]:
        """Get inverted keyword index"""
        if not self._inverted_index:
            self._generate_index()
        return self._inverted_index

    def quick_keyword_match(
        self,
        query: str,
        min_matches: int = 2,
        min_files: int = 1,
        match_threshold: float = 0.3,
    ) -> bool:
        """Check if query matches documents using multiple strategies"""
        query_keywords = set(re.findall(r"\w+", query))
        if not self.case_sensitive:
            query_keywords = {kw.lower() for kw in query_keywords}

        # Inverted index lookup
        matched_files = set()
        for kw in query_keywords:
            if kw in self.inverted_index:
                matched_files.update(self.inverted_index[kw])

        # Multiple matching strategies
        if len(matched_files) >= min_files:
            return True

        if query_keywords:
            # Term frequency check
            max_matches = 0
            for file_info in self.index.values():
                matches = len(query_keywords.intersection(file_info["keywords"]))
                if matches / len(query_keywords) >= match_threshold:
                    return True
                max_matches = max(max_matches, matches)

            if max_matches >= min_matches:
                return True

        return False

    def refresh(self) -> None:
        """Force refresh of the index"""
        with self.lock:
            self._index_cache = None
            self._inverted_index = None
            self._index_hash = None

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the current index"""
        return {
            "last_updated": self._index_timestamp,
            "num_files": len(self.index),
            "num_keywords": len(self.inverted_index),
            "total_size": sum(f["size"] for f in self.index.values()),
        }
