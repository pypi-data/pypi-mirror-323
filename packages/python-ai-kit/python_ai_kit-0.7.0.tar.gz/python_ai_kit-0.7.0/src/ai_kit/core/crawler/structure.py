def get_section_from_url(url: str) -> str:
    """Extract section from URL pattern"""
    # Common prefixes that indicate sections
    sections = {
        'voice-agent': 'voice-agent',
        'tts': 'text-to-speech',
        'stt': 'speech-to-text'
    }
    
    # Check if URL starts with a section prefix
    for prefix, section in sections.items():
        if url.startswith(prefix):
            return section
            
    return 'general'

def get_tree(self) -> str:
    """Generate a tree view of the documentation structure"""
    tree = ["# Documentation Tree\n\n"]
    
    # Group pages by section
    sections = {}
    
    for url, page in self.pages.items():
        section = get_section_from_url(url)
        if section not in sections:
            sections[section] = []
        sections[section].append((url, page))
    
    # Add sections and their pages
    for section, pages in sorted(sections.items()):
        tree.append(f"\n## {section.replace('-', ' ').title()}\n")
        for url, page in sorted(pages, key=lambda x: x[1].title):
            tree.append(f"- [{page.title}]({url}.md)\n")
            
    return "".join(tree) 