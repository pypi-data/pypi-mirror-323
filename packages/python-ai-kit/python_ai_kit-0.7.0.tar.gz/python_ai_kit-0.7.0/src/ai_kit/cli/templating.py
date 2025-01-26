import importlib.resources
import shutil
from pathlib import Path
from rich.console import Console
from ..config import CoreConfig

console = Console()

def copy_dir(source_dir: Path, dest_dir: Path) -> None:
    """Copy directory to the destination directory."""
    if not source_dir.is_dir():
        return
    
    if not dest_dir.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)

    # Handle root .gitignore first
    gitignore_template = source_dir / '.gitignore'
    if gitignore_template.exists():
        # Use the parent of dest_dir (the repo root) for .gitignore
        handle_gitignore(gitignore_template, Path('.gitignore'))

    # Copy every file/subdirectory in source_dir to dest_dir
    for item in source_dir.iterdir():
        if item.is_file():
            # Skip .gitignore since we handled it separately
            if item.name != '.gitignore':
                shutil.copy2(item, dest_dir / item.name)
        elif item.is_dir():
            shutil.copytree(item, dest_dir / item.name) # this is already recursive

    console.print(f"[green]✓ Created directory {CoreConfig.ROOT_DIR}[/green]")

def handle_gitignore(source: Path, dest: Path) -> None:
    """Handle .gitignore file copying with special merge logic."""
    # Read source content
    source_content = source.read_text().splitlines()
    
    # If destination doesn't exist, just copy the source
    if not dest.exists():
        dest.write_text('\n'.join(source_content) + '\n')
        console.print("[green]✓ Created .gitignore file[/green]")
        return
        
    # Read existing content
    dest_content = dest.read_text().splitlines()
    
    # Add our entries if they don't exist
    added = False
    for line in source_content:
        if line and line not in dest_content:
            if not added:
                # Add a blank line and comment if this is our first addition
                if dest_content and dest_content[-1] != '':
                    dest_content.append('')
                dest_content.append('# Added by AI Kit')
                added = True
            dest_content.append(line)
    
    # Write back if we made changes
    if added:
        dest.write_text('\n'.join(dest_content) + '\n')
        console.print("[green]✓ Updated .gitignore file[/green]")