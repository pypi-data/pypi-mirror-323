import os
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from markdownify import markdownify as md
from urllib.parse import urlparse

class HTMLToMarkdownConverter:
    """Converts HTML content to Markdown format"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        
    def convert(self, html: str) -> str:
        """Convert HTML content to Markdown"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try to find main content
        main_content = None
        for selector in ['main', 'article', '[role="main"]', '#content', '.content', '.main-content']:
            content = soup.select_one(selector)
            if content:
                main_content = content
                break
                
        # If no main content found, use body
        if not main_content:
            main_content = soup.body if soup.body else soup
            
        # Remove navigation, header, footer, and other non-content elements
        selectors_to_remove = [
            'nav', 'header', 'footer', '.navigation', '.sidebar', 'style', 'script',
            '#navbar', '#sidebar', '#table-of-contents', '#footer', '.eyebrow',
            '[role="navigation"]', '[role="complementary"]', '.menu', '.search',
            '.social-links', '.pagination', '.breadcrumbs', '.toc'
        ]
        for selector in selectors_to_remove:
            for element in main_content.select(selector):
                element.decompose()
            
        # Clean up empty elements
        for element in main_content.find_all():
            if len(element.get_text(strip=True)) == 0:
                element.decompose()
            elif element.name == 'div' and element.get('class') and any(c in ['flex', 'leading-6'] for c in element.get('class')):
                # Only remove flex containers that look like navigation
                if all(a.get('href', '').startswith('/') for a in element.find_all('a')):
                    element.decompose()
                    
        # Handle code blocks with language info
        for code in main_content.find_all('code'):
            if code.parent.name == 'pre' and code.get('class'):
                classes = code.get('class')
                for class_name in classes:
                    if class_name.startswith('language-'):
                        lang = class_name.replace('language-', '')
                        # Wrap code in language-specific markdown
                        code.string = f"```{lang}\n{code.get_text()}\n```"
                        break
                    
        # Convert to markdown using markdownify
        return md(str(main_content), heading_style="ATX", bullets="-", strip=['script', 'style'])

def convert_page_to_markdown(content: str, output_path: str):
    """Convert HTML content to markdown and save to file"""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Convert HTML to markdown using markdownify
    converter = HTMLToMarkdownConverter(base_url="")
    markdown = converter.convert(content)
    
    # Save markdown content
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

def create_sitemap(structure, output_dir: str) -> str:
    """Create a sitemap file from the document structure"""
    sitemap_path = os.path.join(output_dir, "SUMMARY.md")
    
    with open(sitemap_path, "w") as f:
        f.write("# Documentation\n\n")
        
        # Add pages without sections
        unsectioned_pages = [p for p in structure.pages.values() if not p.section]
        for page in unsectioned_pages:
            filename = os.path.basename(urlparse(page.url).path)
            if not filename:
                filename = "index"
            f.write(f"* [{page.title}]({filename}.md)\n")
            
        # Add sections and their pages
        for section, urls in structure.sections.items():
            f.write(f"\n## {section}\n\n")
            for url in urls:
                page = structure.pages[url]
                filename = os.path.basename(urlparse(page.url).path)
                if not filename:
                    filename = "index"
                f.write(f"* [{page.title}]({filename}.md)\n")
                
    return sitemap_path 