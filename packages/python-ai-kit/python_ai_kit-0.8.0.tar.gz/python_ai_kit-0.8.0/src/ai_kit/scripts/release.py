#!/usr/bin/env python3
"""
Smart release script that uses AI Kit's LiteLLM client to analyze commits and suggest version bumps.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple
from pydantic import BaseModel
from packaging import version
from rich.console import Console
from rich.panel import Panel
import re

from ai_kit.core.llms.litellm_client import StructuredOutputClient

console = Console()

class VersionBump(BaseModel):
    """Schema for version bump response."""
    version: str
    reasoning: str

def run_cmd(cmd: List[str], error_msg: str) -> str:
    """Run command with error handling."""
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.PIPE).strip()
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error:[/] {error_msg}")
        if e.stderr:
            console.print(f"[red]Details:[/] {e.stderr if isinstance(e.stderr, str) else e.stderr.decode()}")
        sys.exit(1)

def validate_release_env():
    """Validate we're on main branch and have commits to release."""
    # Check if git is initialized
    if not Path(".git").is_dir():
        console.print("[red]Error:[/] Not a git repository")
        sys.exit(1)
    
    # Check if we're in CI
    is_ci = os.environ.get("CI") == "true"
    
    # Check remote
    remotes = run_cmd(
        ["git", "remote"], 
        "Failed to check git remotes"
    )
    if "origin" not in remotes:
        console.print("[red]Error:[/] No 'origin' remote configured")
        sys.exit(1)
    
    # Check if we're on main
    current_branch = run_cmd(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        "Failed to get current branch"
    )
    if current_branch != "main":
        console.print("[red]Error:[/] Releases must be done from main branch")
        sys.exit(1)
    
    # In CI, we trust the environment is clean and synced
    if is_ci:
        return
        
    # Check for dirty working directory
    if run_cmd(["git", "status", "--porcelain"], "Failed to check git status"):
        console.print("[red]Error:[/] Working directory is not clean")
        sys.exit(1)
    
    # Check if we can push to main
    run_cmd(
        ["git", "fetch", "origin", "main"], 
        "Failed to fetch from origin"
    )
    
    # Check for unpushed commits
    try:
        diff = run_cmd(
            ["git", "diff", "origin/main...HEAD"],
            "Failed to check for unpushed commits"
        )
        if diff:
            console.print("[red]Error:[/] You have unpushed commits. Please push to main first")
            sys.exit(1)
    except subprocess.CalledProcessError:
        console.print("[red]Error:[/] Failed to compare with origin/main")
        sys.exit(1)

def validate_version_string(ver: str) -> bool:
    """Validate version string format."""
    return bool(re.match(r'^\d+\.\d+\.\d+$', ver))

def validate_version_bump(current: str, new: str):
    """Validate version changes. Only errors on version decrease."""
    if not validate_version_string(current):
        raise ValueError(f"Invalid current version format: {current}")
    if not validate_version_string(new):
        raise ValueError(f"Invalid new version format: {new}")
    
    current_ver = version.parse(current)
    new_ver = version.parse(new)
    
    if new_ver < current_ver:
        raise ValueError(
            f"New version {new} cannot be less than current version {current}"
        )

def analyze_commits(commits: List[str], current_version: str) -> VersionBump:
    """Analyze commits and suggest version bump using LLM."""
    if not commits:
        raise ValueError("No commits provided for analysis")
        
    client = StructuredOutputClient()
    prompt = f"""Given these commits since the last release (current version {current_version}):

{chr(10).join('- ' + c for c in commits)}

Analyze the changes and suggest a semantic version bump (major.minor.patch).

ONLY count changes from the /src directory. This is a monorepo and only changes in the src directory are relevant.

First, list all the files that have changed in the /src directory.

Then, analyze the changes and suggest a semantic version bump (major.minor.patch).

Consider:
- Breaking changes, major refactoring -> major bump
- New features -> minor bump
- Bug fixes/small changes, little features -> patch bump

Return the new version number and a brief explanation."""

    result = client.structured_output_completion(
        messages=[{"role": "user", "content": prompt}],
        schema=VersionBump
    )
    
    # Validate version bump
    validate_version_bump(current_version, result.version)
    return result

def get_current_version() -> str:
    """Get current version from __init__.py"""
    init_path = Path("src/ai_kit/__init__.py")
    if not init_path.exists():
        raise ValueError(f"Version file not found: {init_path}")
        
    version_pattern = r'__version__\s*=\s*["\']([^"\']+)["\']'
    content = init_path.read_text()
    match = re.search(version_pattern, content)
    
    if not match:
        raise ValueError("Version pattern not found in __init__.py")
    
    version_str = match.group(1)
    if not validate_version_string(version_str):
        raise ValueError(f"Invalid version format in __init__.py: {version_str}")
        
    return version_str

def get_commits_since_last_tag() -> List[str]:
    """Get all commits since the last tag, or all commits if no tag exists."""
    current_version = get_current_version()
    current_tag = f"v{current_version}"
    
    # Check for existing tags
    tags = run_cmd(
        ["git", "tag"], 
        "Failed to get git tags"
    ).split()
    
    # Find previous tag if any
    version_tags = [t for t in tags if t.startswith('v') and t != current_tag]
    if version_tags:
        # Sort tags by version number
        version_tags.sort(key=lambda t: version.parse(t.lstrip('v')))
        previous_tag = version_tags[-1]  # Get the highest version
        console.print(f"[yellow]Getting commits since {previous_tag}[/]")
        return run_cmd(
            ["git", "log", f"{previous_tag}..HEAD", "--pretty=format:%s"],
            "Failed to get commits since previous tag"
        ).splitlines()
    else:
        # This is the first tag - get all commits
        console.print("[yellow]No previous tags found - including all commits[/]")
        return run_cmd(
            ["git", "log", "--pretty=format:%s"],
            "Failed to get commit history"
        ).splitlines()

def update_version(new_version: str):
    """Update version in both __init__.py and pyproject.toml"""
    if not validate_version_string(new_version):
        raise ValueError(f"Invalid version format: {new_version}")
        
    current = get_current_version()
    files_to_update = [
        Path("src/ai_kit/__init__.py"),
        Path("pyproject.toml")
    ]
    
    # Verify all files exist
    for path in files_to_update:
        if not path.exists():
            raise ValueError(f"Version file not found: {path}")
    
    # Create backups
    backups = []
    try:
        for path in files_to_update:
            backup_path = path.with_suffix(path.suffix + '.bak')
            path.rename(backup_path)
            backups.append((path, backup_path))
            
            content = backup_path.read_text()
            new_content = content.replace(f'"{current}"', f'"{new_version}"')
            path.write_text(new_content)
            
    except Exception as e:
        console.print(f"[red]Error updating version files: {e}[/]")
        # Restore from backups
        for orig, backup in backups:
            if backup.exists():
                backup.rename(orig)
        sys.exit(1)
    
    # Clean up backups
    for _, backup in backups:
        backup.unlink()

def build_and_publish():
    """Build and publish to PyPI"""
    version = get_current_version()
    tag = f"v{version}"
    is_dry_run = os.environ.get("DRY_RUN") == "true"
    
    if is_dry_run:
        console.print(f"[yellow]DRY RUN:[/] Would publish version {version} to PyPI")
        return
    
    # Check for PyPI token
    if "TWINE_USERNAME" not in os.environ or "TWINE_PASSWORD" not in os.environ:
        console.print("[red]Error:[/] PyPI credentials not found in environment")
        sys.exit(1)
    
    # Clean old builds
    for path in ["dist", "build"]:
        if Path(path).exists():
            run_cmd(["rm", "-rf", path], f"Failed to clean {path} directory")
    
    try:
        # Build
        run_cmd(["python", "-m", "build"], "Failed to build package")
        
        # Upload to PyPI
        run_cmd(["python", "-m", "twine", "upload", "dist/*"], "Failed to upload to PyPI")
        
        # Create and push tag only after successful upload
        console.print(f"\n[bold cyan]Creating and pushing tag {tag}...[/]")
        run_cmd(["git", "tag", tag], f"Failed to create tag {tag}")
        run_cmd(["git", "push", "origin", tag], f"Failed to push tag {tag}")
        
    except Exception as e:
        console.print(f"[red]Error during release: {e}[/]")
        # Clean up tag if it was created
        try:
            subprocess.run(["git", "tag", "-d", tag], check=False)
            subprocess.run(["git", "push", "origin", f":refs/tags/{tag}"], check=False)
        except:
            pass
        raise

def main():
    try:
        is_dry_run = os.environ.get("DRY_RUN") == "true"
        if is_dry_run:
            console.print("[yellow]Running in DRY RUN mode - no changes will be made[/]\n")
        
        # Validate environment first
        validate_release_env()
        
        current_version = get_current_version()
        console.print(f"[bold blue]Current version:[/] {current_version}")
        
        commits = get_commits_since_last_tag()
        if not commits:
            console.print("[yellow]No new commits since last tag[/]")
            sys.exit(0)
            
        # Check if any commits are to main
        try:
            main_commits = run_cmd(
                ["git", "log", "--no-merges", "--format=%H", f"v{current_version}..HEAD"],
                "Failed to check for commits to main"
            ).splitlines()
        except:
            # If tag doesn't exist or other error, get all commits
            main_commits = run_cmd(
                ["git", "log", "--no-merges", "--format=%H"],
                "Failed to check for commits to main"
            ).splitlines()
        
        if not main_commits:
            console.print("[red]Error:[/] No commits to main branch since last release")
            sys.exit(1)
        
        console.print("\n[bold]Analyzing commits...[/]")
        result = analyze_commits(commits, current_version)
        
        # Exit early if version hasn't changed (means no relevant changes in src)
        if result.version == current_version:
            console.print("[yellow]No changes detected in src directory, skipping release[/]")
            sys.exit(0)
        
        # Show version bump suggestion in a panel
        console.print(Panel.fit(
            f"[green]Version:[/] {current_version} → {result.version}\n[cyan]Reasoning:[/] {result.reasoning}",
            title="Version Bump Suggestion",
            border_style="blue"
        ))
        
        # In CI, we auto-approve. Otherwise, ask for confirmation
        should_proceed = os.environ.get("CI") == "true" or \
            console.input("\n[yellow]Proceed with release? [y/N][/] ").lower() == "y"
            
        if not should_proceed:
            console.print("[red]Aborting[/]")
            sys.exit(0)
        
        if is_dry_run:
            console.print("\n[yellow]DRY RUN:[/] Would make the following changes:")
            console.print(f"1. Update version to {result.version} in __init__.py and pyproject.toml")
            console.print(f"2. Create and push version bump commit")
            console.print(f"3. Build and publish to PyPI")
            console.print(f"4. Create and push tag v{result.version}")
            sys.exit(0)
        
        console.print("\n[bold cyan]Updating version numbers...[/]")
        update_version(result.version)
        
        console.print("\n[bold cyan]Committing version bump...[/]")
        run_cmd(["git", "add", "src/ai_kit/__init__.py", "pyproject.toml"], "Failed to stage version files")
        run_cmd(["git", "commit", "-m", f"chore: bump version to {result.version}"], "Failed to commit version bump")
        run_cmd(["git", "push"], "Failed to push version bump")
        
        console.print("\n[bold cyan]Building and publishing...[/]")
        build_and_publish()
        
        console.print(f"\n[bold green]Successfully released v{result.version}! 🎉[/]")
        
    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 