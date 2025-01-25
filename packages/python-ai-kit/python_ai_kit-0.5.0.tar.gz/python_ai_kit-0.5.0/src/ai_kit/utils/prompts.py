"""Utilities for handling prompts and file references."""
import re
from .fs import load_file_content_safe

def process_file_references(text: str) -> str:
    """Replace {{filename}} references with file contents.
    
    Args:
        text: Text containing {{filename}} references to files in the workspace.
              The filename can contain optional whitespace, which will be stripped.
              Example: "{{file.py}}", "{{  file.py  }}", "{{ file.py}}"
        
    Returns:
        Text with file references replaced by their contents, wrapped in markers
    """
    def replace_match(match):
        filepath = match.group(1).strip()  # Strip whitespace from filename
        content = load_file_content_safe(filepath)
        return f"\n=== Content of {filepath} ===\n{content}\n=== End of {filepath} ===\n"
    
    return re.sub(r'\{\{(.+?)\}\}', replace_match, text) 

def load_prompt(path: str) -> str:
    with open(path, "r") as file:
        return file.read()
