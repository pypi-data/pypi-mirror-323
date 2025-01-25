# dircontextgen/core.py
from pathlib import Path
from typing import List, Optional, Dict, Set, Tuple
import os
import fnmatch
from .utils.ignore_patterns import (
    read_ignore_patterns,
    is_path_ignored
)
from .utils.file_handling import (
    is_binary_file,
    get_file_content,
    read_target_patterns,
    is_vcs_directory
)
from .utils.tree_generation import generate_tree

class DocumentationGenerator:
    def __init__(
        self,
        base_dir: str,
        output_file: str = "project_documentation.txt",
        additional_ignore_files: List[str] = None,
        target_file: Optional[str] = None,
        tree_only: bool = False,
        max_file_size: int = 1024*1024,
        exclude_patterns: List[str] = None,
        include_patterns: List[str] = None,
        verbose: bool = False,
        structure_mode: str = "minimal",
        collapse_threshold: int = 10
    ):
        self.base_dir = Path(base_dir)
        self.output_file = Path(output_file)
        self.additional_ignore_files = additional_ignore_files or []
        self.target_file = target_file
        self.tree_only = tree_only
        self.max_file_size = max_file_size
        self.exclude_patterns = exclude_patterns or []
        self.include_patterns = include_patterns or []
        self.verbose = verbose
        self.structure_mode = structure_mode
        self.collapse_threshold = collapse_threshold
        
        # Initialize pattern storage
        self.ignore_patterns: Dict[str, List[str]] = {}
        self.target_patterns: List[str] = []
        
    def _load_patterns(self) -> None:
        """Load all ignore and target patterns."""
        # Load ignore patterns from .gitignore and .dirignore
        self.ignore_patterns = read_ignore_patterns(
            self.base_dir,
            additional_files=self.additional_ignore_files
        )
        
        # Load target patterns if specified
        if self.target_file:
            self.target_patterns = read_target_patterns(self.target_file)
            
        # Add CLI-provided patterns
        self.target_patterns.extend(self.include_patterns)
        
        # Add CLI exclude patterns to root ignore patterns
        base_dir_str = str(self.base_dir.resolve())
        root_ignores = self.ignore_patterns.get(base_dir_str, [])
        root_ignores.extend(self.exclude_patterns)
        self.ignore_patterns[base_dir_str] = root_ignores

    def _should_include_file(self, file_path: Path) -> bool:
        """Determine if a file should be included in the documentation."""
        try:
            # Always exclude VCS directories
            if is_vcs_directory(file_path):
                if self.verbose:
                    print(f"Skipping VCS directory/file: {file_path}")
                return False
                
            abs_file = file_path.resolve()
            abs_base = self.base_dir.resolve()
            rel_path = abs_file.relative_to(abs_base)
            
            # In complete or smart mode, include all non-VCS files
            if self.structure_mode in ("complete", "smart"):
                return True
            
            # Check if file is ignored
            if is_path_ignored(abs_file, self.ignore_patterns, abs_base):
                return False
                
            # If target patterns exist, file must match at least one
            if self.target_patterns:
                return any(
                    fnmatch.fnmatch(str(rel_path), pattern)
                    for pattern in self.target_patterns
                )
                
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Error checking file inclusion for {file_path}: {e}")
            return False

    def _should_include_content(self, file_path: Path) -> bool:
        """Determine if a file's content should be included."""
        if self.tree_only:
            return False
            
        try:
            # Always exclude VCS files
            if is_vcs_directory(file_path):
                return False
                
            # Check file size
            if file_path.stat().st_size > self.max_file_size:
                if self.verbose:
                    print(f"Skipping content of large file: {file_path}")
                return False
                
            # Check if binary
            if is_binary_file(file_path):
                if self.verbose:
                    print(f"Skipping binary file: {file_path}")
                return False
                
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Error checking content inclusion for {file_path}: {e}")
            return False

    def generate(self) -> None:
        """Generate the documentation file."""
        # Load all patterns
        self._load_patterns()
        
        # Generate tree and get matching files
        tree_lines, matching_files = generate_tree(
            self.base_dir,
            self._should_include_file,
            self.verbose,
            self.structure_mode
        )
        
        # Write documentation
        with open(self.output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("Project Documentation\n")
            f.write("===================\n\n")
            
            # Write directory tree
            f.write("Directory Structure\n")
            f.write("------------------\n")
            f.write("\n".join(tree_lines))
            f.write("\n\n")
            
            # Write file contents if not tree_only and in minimal mode
            if not self.tree_only and self.structure_mode == "minimal":
                f.write("File Contents\n")
                f.write("-------------\n")
                
                for file_path in matching_files:
                    if self._should_include_content(file_path):
                        rel_path = file_path.relative_to(self.base_dir)
                        rel_path_posix = rel_path.as_posix()  # Convert to POSIX path
                        content = get_file_content(file_path)
                        
                        if content is not None:
                            f.write(f"\nFile: {rel_path_posix}\n")
                            f.write("-" * 80 + "\n")
                            f.write(content)
                            f.write("\n" + "-" * 80 + "\n")