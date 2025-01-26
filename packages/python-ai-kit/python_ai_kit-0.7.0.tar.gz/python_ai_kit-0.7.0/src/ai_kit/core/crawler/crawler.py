import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
from .converter import HTMLToMarkdownConverter

logger = logging.getLogger(__name__)

@dataclass
class Page:
    """Represents a documentation page"""
    url: str
    title: str
    fs_path: str  # Single source of truth for filesystem path
    section: Optional[str] = None  # Optional logical section
    html: Optional[str] = None

@dataclass
class DocumentStructure:
    """Represents the structure of documentation"""
    pages: Dict[str, Page] = field(default_factory=dict)
    sections: Dict[str, List[str]] = field(default_factory=dict)
    
    def add_page(self, url: str, title: str, fs_path: str, section: Optional[str] = None, html: Optional[str] = None):
        """Add a page to the structure
        
        Args:
            url: Original URL
            title: Page title
            fs_path: Canonical filesystem path (without .md extension)
            section: Optional logical section
            html: Optional HTML content
        """
        # If no section provided, derive it from fs_path
        if not section and '/' in fs_path:
            section = fs_path.rsplit('/', 1)[0]
            
        self.pages[url] = Page(url=url, title=title, fs_path=fs_path, section=section, html=html)
        if section:
            if section not in self.sections:
                self.sections[section] = []
            self.sections[section].append(url)
            
    def get_tree(self) -> str:
        """Get a tree representation of the documentation structure"""
        tree = ["Documentation Tree\n"]
        tree.append("\n└── Documentation")
        
        # First add pages without sections
        unsectioned_pages = [p for p in self.pages.values() if not p.section]
        for page in sorted(unsectioned_pages, key=lambda p: p.title):
            filename = f"{page.fs_path}.md"
            tree.append(f"    ├── [{page.title}]({filename})")
        
        # Then add sections and their pages
        for section_name, urls in sorted(self.sections.items()):
            tree.append(f"    └── {section_name}")
            for url in urls:
                page = self.pages[url]
                filename = f"{page.fs_path}.md"
                tree.append(f"        ├── [{page.title}]({filename})")
                
        return "\n".join(tree)

@dataclass
class StartCrawl:
    url: str
    max_pages: int

@dataclass
class PageFetched:
    url: str
    html: str

@dataclass
class PageProcessed:
    url: str
    title: str
    links: List[str]
    section: Optional[str] = None
    html: Optional[str] = None

@dataclass
class CrawlComplete:
    total_pages: int

@dataclass
class ShutdownMessage:
    """Sentinel message to indicate actor shutdown"""
    pass

class Actor:
    """Base class for actors in the system"""
    def __init__(self):
        self.mailbox = asyncio.Queue()
        self._running = True
        
    async def start(self):
        """Start the actor"""
        await self.run()
        
    async def stop(self):
        """Stop the actor gracefully"""
        self._running = False
        await self.mailbox.put(ShutdownMessage())
        
    async def run(self):
        """Main actor loop"""
        while self._running:
            msg = await self.mailbox.get()
            try:
                if isinstance(msg, ShutdownMessage):
                    self.mailbox.task_done()
                    break
                await self.handle_message(msg)
                self.mailbox.task_done()
            except Exception as e:
                logger.error(f"Error in actor: {e}")
                self.mailbox.task_done()
            
    async def handle_message(self, message):
        """Handle an incoming message"""
        pass

class FetcherActor(Actor):
    """Actor responsible for fetching pages"""
    def __init__(self, base_url: str, queue_size: int = 100):
        super().__init__()
        self.base_url = base_url
        self.result_queue = asyncio.Queue(maxsize=queue_size)
        self.session = None  # Will be set by supervisor
        
    async def handle_message(self, url: str):
        """Handle a URL to fetch"""
        try:
            if not self.session:
                logger.error(f"No session available for {url}")
                raise RuntimeError(f"No session available for {url}")
                
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    await self.result_queue.put((url, html))
                    logger.info(f"Fetched {url}")
                else:
                    error_msg = f"HTTP {response.status} fetching {url}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            raise  # Re-raise to propagate error

class ProcessorActor(Actor):
    """Actor responsible for processing HTML content"""
    def __init__(self, base_url: str, stay_within_scope: bool = True):
        super().__init__()
        self.base_url = base_url
        self.stay_within_scope = stay_within_scope
        
    def _is_same_domain(self, url: str) -> bool:
        """Check if URL is from the same domain as base_url"""
        base_parts = urlparse(self.base_url)
        url_parts = urlparse(url)
        return base_parts.netloc == url_parts.netloc

    def _is_within_scope(self, url: str) -> bool:
        """Check if URL is within the allowed directory scope.
        
        For example, if base_url is https://website.com/docs/introduction,
        then any URL under https://website.com/docs/ is allowed.
        
        Relative URLs (starting with /) are always considered in scope since
        they are relative to the same domain.
        """
        # Handle relative URLs (starting with /)
        if url.startswith('/'):
            return True
            
        base_parts = urlparse(self.base_url)
        url_parts = urlparse(url)
        
        # Get base scope by removing the last path component
        base_scope = base_parts.path.rsplit('/', 1)[0]  # e.g. '/docs'
        
        # Only check that url_parts.path starts with base_scope
        return (base_parts.netloc == url_parts.netloc and
                url_parts.path.startswith(base_scope))
        
    async def handle_message(self, message: tuple):
        """Process a fetched page"""
        url, html = message
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title - try meta title first, then title tag, then URL
        title = None
        meta_title = soup.find('meta', property='og:title')
        if meta_title:
            title = meta_title.get('content')
        if not title:
            title = soup.title.string if soup.title else url.split('/')[-1]
        
        # Extract main content
        main_content = None
        # Try common content containers
        for container in ['main', 'article', '[role="main"]', '#content', '.content', '.main-content']:
            content = soup.select_one(container)
            if content:
                main_content = content
                break
        # Fallback to body if no content container found
        if not main_content:
            main_content = soup.body if soup.body else soup
        
        # Extract links
        links = []
        for a in soup.find_all('a', href=True):
            link = urljoin(url, a['href'])
            # Only include links from same domain, optionally check scope, and skip anchors
            if (self._is_same_domain(link) and 
                (not self.stay_within_scope or self._is_within_scope(link)) and 
                not link.endswith(('#', '#content'))):
                # Normalize the URL
                link = link.split('#')[0].rstrip('/')
                links.append(link)
                
        # Extract section if available
        section = None
        # Try common section indicators
        for section_class in ['section-title', 'breadcrumb', 'category']:
            section_elem = soup.find(class_=section_class)
            if section_elem:
                section = section_elem.get_text(strip=True)
                break
            
        logger.info(f"Processed {url}")
        return PageProcessed(url=url, title=title, links=links, section=section, html=str(main_content))

class CrawlSupervisor:
    """Supervisor that coordinates the crawling process"""
    def __init__(self, max_fetchers: int = 3, max_processors: int = 2, queue_size: int = 100, restrict_to_docs: bool = True):
        self.max_fetchers = max_fetchers
        self.max_processors = max_processors
        self.queue_size = queue_size
        self.structure = DocumentStructure()
        self.seen_urls = set()
        self.tasks = []
        self.base_url = None
        self.fetchers = []
        self.processors = []
        self.session = None
        self.restrict_to_docs = restrict_to_docs

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and trailing slashes"""
        # Remove fragment
        url = url.split('#')[0]
        # Remove trailing slash
        url = url.rstrip('/')
        # Remove query parameters
        url = url.split('?')[0]
        return url
        
    def _get_section_path(self, url: str) -> str:
        """Extract section from URL pattern"""
        try:
            # Parse URL and get path
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            
            # Split path into parts
            parts = path.split('/')
            
            # Handle special cases
            if len(parts) <= 2 or parts[-1] == "introduction":  # Skip 'docs' prefix and handle introduction
                return ""
            
            # Remove 'docs' prefix if present
            if parts[0] == "docs":
                parts = parts[1:]
            
            # Check for known section indicators
            if any(x in parts[0] for x in ['voice-agent', 'tts', 'stt']):
                return parts[0]
            elif any(x in parts[0] for x in ['language', 'model', 'diarization', 'encoding']):
                return 'features'
            
            # For guides and other multi-level sections, include up to the last part
            if len(parts) > 2 and parts[0] in ['guides', 'api-reference']:
                return '/'.join(parts[:-1])  # Join all parts except the last one
            
            # Use first remaining directory as section
            return parts[0]
        except Exception as e:
            logger.error(f"Error getting section path: {e}")
            return ""

    def _get_clean_path(self, url: str) -> str:
        """Get clean path for storage, without domain.
        This is the single source of truth for filesystem paths.
        
        Args:
            url: Full URL or relative path
            
        Returns:
            Clean path suitable for filesystem (without .md extension)
        """
        try:
            if url.startswith('http'):
                parsed = urlparse(url)
                path = parsed.path.strip('/')
                
                # Handle empty path
                if not path:
                    return 'index'
                
                # Split path into parts
                parts = path.split('/')
                
                # Remove API version prefixes if present
                if parts[0] in ('v0', 'v1'):
                    parts = parts[1:]
                
                # Join parts back together
                return '/'.join(parts)
            return url
        except Exception as e:
            logger.error(f"Error cleaning URL {url}: {e}")
            return None
        
    def _simple_check_is_docs(self, url: str) -> bool:
        keywords = ['docs', 'documentation', 'api', 'reference', 'guide', 'tutorial', 'quickstart', 'getting-started', 'developer']
        return any(keyword in url.lower() for keyword in keywords)
        
    def _init_actors(self, base_url: str):
        """Initialize actors with base URL"""
        self.base_url = self._normalize_url(base_url)
        self.fetchers = [FetcherActor(self.base_url, self.queue_size) for _ in range(self.max_fetchers)]
        self.processors = [ProcessorActor(self.base_url) for _ in range(self.max_processors)]
        
    async def start(self, start_url: str, max_pages: int = 10) -> DocumentStructure:
        """Start the crawling process"""
        # Initialize actors
        if self.restrict_to_docs:
            if not self._simple_check_is_docs(start_url):
                logger.error(f"Start URL {start_url} does not contain docs keywords")
                raise ValueError(f"Start URL {start_url} does not contain docs keywords")

        self._init_actors(start_url)
        
        # Create shared session
        self.session = aiohttp.ClientSession()
        
        try:
            # Share session with fetchers
            for fetcher in self.fetchers:
                fetcher.session = self.session
            
            # Start actors with proper task management
            self.tasks = []
            for fetcher in self.fetchers:
                self.tasks.append(asyncio.create_task(fetcher.start()))
            for processor in self.processors:
                self.tasks.append(asyncio.create_task(processor.start()))
            
            # Add initial URL
            start_url = self._normalize_url(start_url)
            self.seen_urls.add(start_url)
            await self._round_robin_send(self.fetchers, start_url)
            
            # Process pages until done
            current_fetcher = 0
            urls_to_process = set([start_url])  # Track URLs we need to process
            
            while urls_to_process and len(self.structure.pages) < max_pages:
                # Get result from any fetcher
                for fetcher in self.fetchers:
                    try:
                        url, html = await asyncio.wait_for(fetcher.result_queue.get(), timeout=1.0)
                        url = self._normalize_url(url)
                        urls_to_process.discard(url)  # Remove from processing set
                        
                        # Skip if we've already processed this URL
                        if url in self.structure.pages:
                            continue
                        
                        # Process the page
                        processor = self.processors[current_fetcher % len(self.processors)]
                        current_fetcher += 1
                        
                        result = await processor.handle_message((url, html))
                        
                        # Get section path from URL
                        section = self._get_section_path(url)
                        
                        # Use clean path for storage
                        clean_url = self._get_clean_path(url)
                        
                        # Update structure
                        if clean_url:  # Only store docs pages
                            # Use clean_url as both the key and fs_path
                            self.structure.add_page(
                                url=url,  # Original URL as key
                                title=result.title,
                                fs_path=clean_url,  # Clean path for filesystem
                                section=section,  # Optional logical section
                                html=result.html
                            )
                        
                        # Queue new URLs
                        for link in result.links:
                            link = self._normalize_url(link)
                            if link not in self.seen_urls and len(self.structure.pages) < max_pages:
                                self.seen_urls.add(link)
                                urls_to_process.add(link)  # Add to processing set
                                await self._round_robin_send(self.fetchers, link)
                                
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"Error processing page: {e}")
                        
                # Check if we're done - no more URLs to process and all fetchers are empty
                if not urls_to_process and all(f.result_queue.empty() for f in self.fetchers):
                    break
                    
        finally:
            # First stop all actors
            for fetcher in self.fetchers:
                await fetcher.stop()
            for processor in self.processors:
                await processor.stop()
                
            # Wait for all tasks to complete
            for task in self.tasks:
                try:
                    await asyncio.wait_for(task, timeout=5.0)
                except asyncio.TimeoutError:
                    task.cancel()
                except Exception as e:
                    logger.error(f"Error during task cleanup: {e}")
                    task.cancel()
                    
            # Finally close the session
            if self.session:
                await self.session.close()
            
        return self.structure
        
    async def _round_robin_send(self, actors, message):
        """Send a message to actors in round-robin fashion"""
        least_busy = min(actors, key=lambda a: a.mailbox.qsize())
        await least_busy.mailbox.put(message)

    def save_markdown_files(self, output_dir: str) -> None:
        """Save all pages as markdown files in the output directory."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save README with table of contents
        readme_path = os.path.join(output_dir, "README.md") 
        with open(readme_path, "w") as f:
            f.write(self.structure.get_tree())
        
        # Create converter instance
        converter = HTMLToMarkdownConverter(self.base_url)
        
        for url, page in self.structure.pages.items():
            if not page.html:
                continue
                
            # Split fs_path into directory parts and filename
            fs_parts = page.fs_path.split('/')
            if len(fs_parts) > 1:
                # Create directory path from all but the last part
                dir_path = os.path.join(output_dir, *fs_parts[:-1])
                filename = fs_parts[-1]
            else:
                dir_path = output_dir
                filename = fs_parts[0] if fs_parts else 'index'
                
            # Ensure filename has .md extension
            if not filename.endswith('.md'):
                filename += '.md'
                
            # Create directory structure
            os.makedirs(dir_path, exist_ok=True)
            
            # Convert HTML to markdown
            markdown = converter.convert(page.html)
            
            # Save the file
            file_path = os.path.join(dir_path, filename)
            with open(file_path, 'w') as f:
                f.write(f"# {page.title}\n\n")
                f.write(markdown)

def get_path_parts(url: str) -> str:
    """Extract filename from URL path based on sitemap structure
    
    Args:
        url: Clean URL path like 'getting-started'
        
    Returns:
        Filename with .md extension
    """
    # Just use the last part as filename
    filename = url.split('/')[-1]
    
    # Add .md extension if not present
    if not filename.endswith('.md'):
        filename = f"{filename}.md"
        
    return filename 