import os
import re
import time
from datetime import datetime
from urllib.parse import urlparse, unquote

def sanitize_filename(name: str) -> str:
    """Convert a string to a safe filename"""
    # Handle special cases first
    if name.lower() == 'c++':
        return 'cpp'
    
    # Replace spaces with hyphens
    name = name.replace(' ', '-')
    # Remove or replace special characters
    name = re.sub(r'[^\w\-\.]', '', name)
    # Convert to lowercase
    name = name.lower()
    # Replace multiple hyphens with single hyphen
    name = re.sub(r'-+', '-', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    return name

def get_output_path(url: str, base_dir: str) -> tuple[str, str]:
    """Get the output directory path and filename for a URL"""
    # Parse URL and get path
    parsed = urlparse(unquote(url))
    path = parsed.path.strip('/')
    
    if not path:
        return base_dir, "index.md"
    
    # Split path into parts and sanitize
    parts = [sanitize_filename(part) for part in path.split('/')]
    
    # Last part becomes the filename
    filename = parts[-1]
    if not filename.endswith('.md'):
        filename = f"{filename}.md"
    
    # Rest becomes directory structure
    if len(parts) > 1:
        dir_path = os.path.join(base_dir, *parts[:-1])
    else:
        dir_path = base_dir
        
    return dir_path, filename

def create_output_dir(url: str, base_dir: str) -> str:
    """Create output directory for documentation"""
    # Check if base directory exists
    if not os.path.exists(base_dir):
        raise Exception(f"Base directory does not exist: {base_dir}")
    
    # Parse domain from URL
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    # Remove www. and port number if present
    if domain.startswith('www.'):
        domain = domain[4:]
    domain = domain.split(':')[0]
    
    # Convert domain to directory name
    dir_name = domain.replace('.', '-')
    
    # Add timestamp with microseconds for uniqueness
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    output_dir = os.path.join(base_dir, f"{dir_name}-{timestamp}")
    
    # Create main output directory
    os.makedirs(output_dir)  # Don't use exist_ok=True to ensure uniqueness
    
    # Create nested directories if needed
    dir_path, _ = get_output_path(url, output_dir)
    if dir_path != output_dir:
        os.makedirs(dir_path, exist_ok=True)
    
    return output_dir 