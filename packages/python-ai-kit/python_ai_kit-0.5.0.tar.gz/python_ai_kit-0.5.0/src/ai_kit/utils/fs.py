"""Filesystem utilities for ai-kit."""
import os
import stat
from pathlib import Path
from typing import Optional
from ..config import CoreConfig


class WorkspaceError(Exception):
    """Custom exception for workspace-related errors."""
    pass

def remove_file(file_path: Path) -> None:
    """Remove a single file, changing permissions and retrying if needed."""
    try:
        file_path.unlink()
    except PermissionError:
        os.chmod(file_path, stat.S_IWRITE)
        file_path.unlink()
    except FileNotFoundError:
        pass

def remove_dir(dir_path: Path) -> None:
    """Remove a single directory, changing permissions and retrying if needed."""
    try:
        dir_path.rmdir()
    except PermissionError:
        os.chmod(dir_path, stat.S_IWRITE)
        dir_path.rmdir()
    except OSError as e:
        raise e

def remove_tree(root: Path) -> None:
    """Recursively remove a directory tree, handling read-only files/directories."""
    if not root.exists():
        return
    if not root.is_dir():
        raise ValueError(f"{root} is not a directory.")

    # Walk bottom-up
    for dirpath, dirnames, filenames in os.walk(str(root), topdown=False):
        # Remove files first
        for filename in filenames:
            file_path = Path(dirpath) / filename
            remove_file(file_path)

        # Then remove directories
        for dirname in dirnames:
            dir_path = Path(dirpath) / dirname
            remove_dir(dir_path)

    # Finally remove the root folder
    remove_dir(root)

def find_workspace_root(start_path: Optional[Path] = None) -> Path:
    """
    Finds the workspace root by searching for standard project markers starting from
    the given start_path and moving upwards in the directory tree.

    Args:
        start_path (Optional[Path]): The directory to start searching from.
                                      Defaults to the current working directory.

    Returns:
        Path: The workspace root path.

    Raises:
        WorkspaceError: If no workspace root indicators are found in any parent directory.
    """
    if start_path is None:
        current_path = Path.cwd()
    else:
        current_path = start_path.resolve()

    # Standard project markers in order of preference
    root_markers = [".git", "pyproject.toml"]

    for parent in [current_path] + list(current_path.parents):
        # Check each marker
        for marker in root_markers:
            if (parent / marker).exists():
                return parent

    raise WorkspaceError("Workspace root not found. Ensure you are in a project with version control or a pyproject.toml file.")

def join_workspace_path(*args: str) -> Path:
    """
    Joins one or more path components to the workspace root.

    Args:
        *args (str): Path components to join.

    Returns:
        Path: The combined workspace path.

    Raises:
        WorkspaceError: If the workspace root cannot be found.
    """
    workspace_root = find_workspace_root()
    return workspace_root.joinpath(*args).resolve()

def get_relative_path(path: Path) -> Path:
    """
    Gets the relative path from the workspace root to the given path.

    Args:
        path (Path): The absolute path.

    Returns:
        Path: The relative path from the workspace root.

    Raises:
        WorkspaceError: If the workspace root cannot be found.
        ValueError: If the given path is not inside the workspace.
    """
    workspace_root = find_workspace_root()
    try:
        return path.relative_to(workspace_root)
    except ValueError as e:
        raise ValueError(f"The path '{path}' is not inside the workspace root '{workspace_root}'.") from e

def ensure_workspace_path(path: Path) -> Path:
    """
    Ensures that the given path is within the workspace. If the path is relative,
    it is made absolute by joining with the workspace root.

    Args:
        path (Path): The path to ensure.

    Returns:
        Path: An absolute path within the workspace.

    Raises:
        WorkspaceError: If the workspace root cannot be found.
    """
    if not path.is_absolute():
        return join_workspace_path(path.parts[0], *path.parts[1:])
    return path

def list_workspace_files(extension: Optional[str] = None) -> list[Path]:
    """
    Lists all files in the workspace. Optionally filters by file extension.

    Args:
        extension (Optional[str]): The file extension to filter by (e.g., '.txt').
                                   If None, all files are listed.

    Returns:
        list[Path]: A list of file paths within the workspace.

    Raises:
        WorkspaceError: If the workspace root cannot be found.
    """
    workspace_root = find_workspace_root()
    if extension:
        return list(workspace_root.rglob(f"*{extension}"))
    return list(workspace_root.rglob("*.*"))

def load_file_content(workspace_path: str) -> str:
    """Load file content from workspace path (relative to workspace root).
    
    Args:
        workspace_path: Path relative to workspace root
        
    Returns:
        Content of the file as string
        
    Raises:
        WorkspaceError: If workspace root cannot be found
        OSError: If file cannot be read
    """
    full_path = join_workspace_path(workspace_path)
    return full_path.read_text()

def load_file_content_safe(workspace_path: str) -> str:
    """Load file content with error handling, returning error message on failure.
    
    Args:
        workspace_path: Path relative to workspace root
        
    Returns:
        Content of the file as string, or error message if file cannot be read
    """
    try:
        return load_file_content(workspace_path)
    except (WorkspaceError, OSError) as e:
        return f"Error loading {workspace_path}: {str(e)}" 