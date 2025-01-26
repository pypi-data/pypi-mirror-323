from typing import Set, Dict, List, Optional
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import asyncio

@dataclass
class ProcessedPage:
    """Represents a processed documentation page"""
    url: str
    title: str
    html: str
    links: Set[str]
    section: Optional[str] = None

class AsyncProcessor:
    """Asynchronous processor for HTML content"""
    
    def __init__(self, max_concurrent: int = 5):
        """Initialize processor with concurrency limit"""
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    def _get_title(self, soup: BeautifulSoup) -> str:
        """Extract page title from soup"""
        title = soup.find('title')
        if title:
            return title.text.strip()
        h1 = soup.find('h1')
        if h1:
            return h1.text.strip()
        return "Untitled"
    
    def _is_same_domain(self, url: str, base_url: str) -> bool:
        """Check if URL is from the same domain as base_url"""
        url_parts = urlparse(url)
        base_parts = urlparse(base_url)
        return url_parts.netloc == base_parts.netloc and url_parts.scheme == base_parts.scheme
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract all links from soup that are on the same domain"""
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/'):
                href = urljoin(base_url, href)
            if href.startswith('http') and self._is_same_domain(href, base_url):
                links.add(href)
        return links
    
    def _extract_section(self, soup, url: str) -> Optional[str]:
        """Extract section from the page"""
        # Try to find section in nav
        nav = soup.find('nav')
        if nav:
            # First try h2 in nav
            section_header = nav.find('h2')
            if section_header and section_header.get_text(strip=True) == "Getting Started":
                return section_header.get_text(strip=True)
            
            # Then try other section indicators
            for section in nav.find_all(['div', 'span'], class_=lambda x: x and ('section' in x.lower() or 'category' in x.lower())):
                text = section.get_text(strip=True)
                if text == "Getting Started":
                    return text
            
        # Try to find section in breadcrumbs
        breadcrumbs = soup.find(class_='breadcrumbs')
        if breadcrumbs:
            items = breadcrumbs.find_all('li')
            if len(items) > 1:
                text = items[-2].get_text(strip=True)
                if text == "Getting Started":
                    return text
            
        # Try to find section in sidebar
        sidebar = soup.find(class_=lambda x: x and ('sidebar' in x.lower() or 'menu' in x.lower()))
        if sidebar:
            active = sidebar.find(class_='active')
            if active:
                parent = active.find_parent(['div', 'ul'])
                if parent:
                    header = parent.find_previous_sibling(['h2', 'h3', 'div'])
                    if header and header.get_text(strip=True) == "Getting Started":
                        return header.get_text(strip=True)
                    
        # No section found
        return None
    
    async def process_html(self, url: str, html: str) -> ProcessedPage:
        """Process HTML content and extract structured information"""
        async with self.semaphore:
            soup = BeautifulSoup(html, 'html.parser')
            
            title = self._get_title(soup)
            links = self._extract_links(soup, url)
            section = self._extract_section(soup, url)
            
            return ProcessedPage(
                url=url,
                title=title,
                html=html,
                links=links,
                section=section
            )

    async def process_batch(self, pages: List[tuple[str, str]]) -> List[ProcessedPage]:
        """Process a batch of pages concurrently"""
        tasks = []
        for url, html in pages:
            task = asyncio.create_task(self.process_html(url, html))
            tasks.append(task)
        
        return await asyncio.gather(*tasks) 