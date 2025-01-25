"""Crawler command implementation."""

import click
import asyncio
from typing import Optional
from rich.console import Console
from datetime import datetime
import os
from pathlib import Path
from ...utils.web import crawl_docs, get_domain_dir, check_existing_docs, has_site_updated, clean_old_caches

console = Console()

async def execute_crawler(url: str, force: bool = False, max_pages: int = 100, max_age_days: int = 30) -> None:
    """Execute crawler command."""
    try:
        # Get standardized directory name from domain
        domain_dir = get_domain_dir(url)
        domain_path = Path(domain_dir)
        
        # Clean old caches
        if domain_path.exists():
            clean_old_caches(domain_path, max_age_days)
        
        # Check for existing docs unless force flag is used
        if not force:
            existing = check_existing_docs(domain_dir)
            if existing:
                existing_path = Path(existing)
                if not has_site_updated(url, existing_path):
                    console.print(f"Found existing docs at: {existing}")
                    console.print("Use --force to re-crawl")
                    return
                else:
                    console.print("Site has been updated since last crawl")
        
        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_dir = os.path.join(domain_dir, timestamp)
        os.makedirs(domain_dir, exist_ok=True)
        
        try:
            # Run the crawler
            await crawl_docs(url, output_dir, max_pages)
            console.print(f"\nDocs saved successfully to: {output_dir}")
        except Exception as e:
            # Clean up domain directory if empty
            try:
                if os.path.exists(domain_dir) and not os.listdir(domain_dir):
                    os.rmdir(domain_dir)
            except Exception:
                pass  # Ignore cleanup errors
            raise
            
    except Exception as e:
        console.print(f"[red]Error during crawling: {str(e)}[/red]")

def crawler_command(url: str, force: bool = False, max_pages: int = 100, max_age_days: int = 30) -> None:
    """CLI command for crawler functionality."""
    asyncio.run(execute_crawler(url, force, max_pages, max_age_days)) 