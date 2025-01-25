# dircontextgen/utils/tree_generation.py
from pathlib import Path
from typing import Callable, List, Tuple, Set, Dict
from collections import defaultdict
import os

def should_collapse_directory(path: Path, file_count_threshold: int = 10) -> Tuple[bool, int]:
    """
    Determine if a directory should be collapsed in smart mode.
    Returns (should_collapse, file_count).
    """
    try:
        files = list(path.rglob('*'))
        file_count = sum(1 for f in files if f.is_file())
        
        # Collapse if too many files
        if file_count > file_count_threshold:
            return True, file_count
            
        # Check for common large directories
        if path.name.lower() in {
            'node_modules', 'logs', 'temp', 'cache', 
            'build', 'dist', 'target', 'out',
            '__pycache__', '.pytest_cache'
        }:
            return True, file_count
            
        return False, file_count
    except Exception:
        return True, 0

def generate_tree(
    base_dir: Path,
    include_filter: Callable[[Path], bool],
    verbose: bool = False,
    structure_mode: str = "minimal"
) -> Tuple[List[str], Set[Path]]:
    """Generate a tree representation of the directory structure.
    
    Args:
        base_dir: Base directory to start from
        include_filter: Function to determine if a file should be included
        verbose: Enable verbose output
        structure_mode: One of "minimal", "complete", or "smart"
    """
    if structure_mode == "smart":
        return [
            "Directory Structure (Smart Mode) - Coming Soon",
            "---------------------------------------------",
            "This feature is under development and will incorporate",
            "AI-powered context-aware directory analysis."
        ], set()

    tree_lines = []
    matching_files = set()

    def _generate_tree_recursive(
        current_dir: Path,
        prefix: str = "",
        is_last: bool = True,
    ) -> None:
        """Recursively generate tree structure."""
        try:
            # Get directory contents
            items = sorted(current_dir.iterdir(), key=lambda x: (x.is_file(), x.name))

            if structure_mode == "minimal":
                # Only show items that pass the filter
                items = [item for item in items if include_filter(item)]
            else:  # complete mode
                from .file_handling import is_vcs_directory
                items = [item for item in items if not is_vcs_directory(item)]

            # Process each item
            for i, item in enumerate(items):
                is_last_item = (i == len(items) - 1)

                # Generate the line prefix
                if current_dir != base_dir:
                    line_prefix = prefix + ("└── " if is_last_item else "├── ")
                else:
                    line_prefix = prefix

                # Add item to tree
                tree_lines.append(f"{line_prefix}{item.name}")

                # Process directory contents
                if item.is_dir():
                    new_prefix = prefix + ("    " if is_last_item else "│   ")
                    _generate_tree_recursive(item, new_prefix, is_last_item)
                elif structure_mode == "minimal" and include_filter(item):
                    matching_files.add(item)
                elif structure_mode == "complete":
                    matching_files.add(item)

        except Exception as e:
            if verbose:
                print(f"Error accessing {current_dir}: {e}")

    # Generate the tree
    _generate_tree_recursive(base_dir)
    
    return tree_lines, matching_files