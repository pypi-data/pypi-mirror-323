# dircontextgen/utils/ignore_patterns.py
from pathlib import Path
from typing import Dict, List, Optional
import os
import fnmatch

from .file_handling import is_vcs_directory

def read_ignore_patterns(
    base_dir: Path,
    additional_files: Optional[List[str]] = None
) -> Dict[str, List[str]]:
    """Read ignore patterns from .gitignore and .dirignore files."""
    patterns: Dict[str, List[str]] = {}
    additional_files = additional_files or []
    
    def read_patterns_from_file(ignore_file: Path) -> List[str]:
        """Read patterns from a single ignore file."""
        try:
            with open(ignore_file, 'r', encoding='utf-8') as f:
                return [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith('#')
                ]
        except Exception as e:
            print(f"Warning: Error reading ignore file {ignore_file}: {e}")
            return []
    
    # Walk through directory tree
    for dirpath, _, _ in os.walk(base_dir):
        current_dir = Path(dirpath).resolve()
        dir_patterns = []
        
        # Check for .gitignore and .dirignore
        for ignore_file in ['.gitignore', '.dirignore']:
            ignore_path = current_dir / ignore_file
            if ignore_path.is_file():
                dir_patterns.extend(read_patterns_from_file(ignore_path))
        
        # Add patterns from additional ignore files
        for ignore_file in additional_files:
            ignore_path = current_dir / ignore_file
            if ignore_path.is_file():
                dir_patterns.extend(read_patterns_from_file(ignore_path))
        
        if dir_patterns:
            patterns[str(current_dir)] = dir_patterns
    
    return patterns

def is_path_ignored(file_path: Path, ignore_patterns: Dict[str, List[str]], base_dir: Path) -> bool:
    """Check if a path should be ignored based on ignore patterns."""
    if is_vcs_directory(file_path):
        return True
    
    abs_base = base_dir.resolve()
    try:
        rel_path = file_path.relative_to(abs_base)
    except ValueError:
        # File outside base directory
        return True
        
    rel_path_str = str(rel_path).replace('\\', '/')
    current_dir = file_path.parent.resolve()

    # Check patterns from all relevant directories
    while True:
        dir_str = str(current_dir)
        patterns = ignore_patterns.get(dir_str, [])
        
        for pattern in patterns:
            pattern = pattern.strip()
            if not pattern:
                continue

            # Handle directory patterns
            if pattern.endswith('/'):
                dir_pattern = pattern[:-1]
                if any(fnmatch.fnmatch(part, dir_pattern) for part in rel_path.parts):
                    return True
                    
            # Handle root directory patterns
            elif pattern.startswith('/'):
                try:
                    local_path = rel_path.relative_to(current_dir.relative_to(abs_base))
                except ValueError:
                    continue
                    
                if fnmatch.fnmatch(str(local_path), pattern[1:]):
                    return True
                    
            # Normal pattern matching
            else:
                if fnmatch.fnmatch(str(rel_path), pattern):
                    return True
                # Also check parent directory patterns
                if '/' in pattern and fnmatch.fnmatch(str(rel_path), f"*/{pattern}"):
                    return True

        if current_dir == abs_base:
            break
            
        current_dir = current_dir.parent

    return False