"""Utilities for handling prompts and file references."""
import re
from pathlib import Path
from .fs import load_file_content_safe, WorkspaceError, join_workspace_path
from ..config import CoreConfig

def process_file_references(text: str) -> str:
    """Replace {{filename}} references with file contents.
    
    Args:
        text: Text containing {{filename}} references to files in the workspace.
              The filename can contain optional whitespace, which will be stripped.
              Example: "{{file.py}}", "{{  file.py  }}", "{{ file.py}}"
              If a directory is referenced, all files within it (recursively) will be included.
              Only files with extensions in CoreConfig.SUPPORTED_FILE_EXTENSIONS will be processed.
        
    Returns:
        Text with file references replaced by their contents, wrapped in markers.
        If a file cannot be loaded, includes an error message instead of the content.
        For directories, includes the content of all supported files within, each wrapped in markers.
        Files with unsupported extensions will be skipped with an error message.
    """
    def replace_match(match):
        filepath = match.group(1).strip()
        try:
            full_path = join_workspace_path(filepath)
            if full_path.is_dir():
                contents = []
                workspace_root = join_workspace_path()
                for child_path in full_path.rglob('*'):
                    if child_path.is_file() and child_path.suffix in CoreConfig.SUPPORTED_FILE_EXTENSIONS:
                        child_rel_path = child_path.relative_to(workspace_root)
                        content = load_file_content_safe(str(child_rel_path))
                        contents.append(f"\n=== Content of {child_rel_path} ===\n{content}\n=== End of {child_rel_path} ===\n")
                return ''.join(contents)
            else:
                # Check if the file has a supported extension
                if full_path.suffix not in CoreConfig.SUPPORTED_FILE_EXTENSIONS:
                    return f"\n=== Error loading {filepath} ===\nFile extension {full_path.suffix} is not supported. Supported extensions: {CoreConfig.SUPPORTED_FILE_EXTENSIONS}\n=== End of {filepath} ===\n"
                content = load_file_content_safe(filepath)
                return f"\n=== Content of {filepath} ===\n{content}\n=== End of {filepath} ===\n"
        except WorkspaceError as e:
            return f"\n=== Error loading {filepath} ===\n{str(e)}\n=== End of {filepath} ===\n"
        except Exception as e:
            return f"\n=== Error processing {filepath} ===\n{str(e)}\n=== End of {filepath} ===\n"
    
    return re.sub(r'\{\{(.+?)\}\}', replace_match, text)

def load_prompt(path: str) -> str:
    with open(path, "r") as file:
        return file.read()
