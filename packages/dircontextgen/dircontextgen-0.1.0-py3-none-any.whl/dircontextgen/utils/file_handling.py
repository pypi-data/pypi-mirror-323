# dircontextgen/utils/file_handling.py
from pathlib import Path
from typing import Optional, Set, List

def get_vcs_directories() -> Set[str]:
    """Return a set of version control system directories to exclude."""
    return {
        '.git',           # Git
        '.svn',          # Subversion
        '.hg',           # Mercurial
        '.bzr',          # Bazaar
        'CVS',           # CVS
        '_darcs',        # Darcs
        '.fossil',       # Fossil
        '.pijul',        # Pijul
        '.repo',         # Android repo tool
    }

def get_text_file_extensions() -> Set[str]:
    """Return a set of common text file extensions."""
    return {
        # Web development
        '.html', '.htm', '.css', '.scss', '.sass', '.less', '.js', '.jsx',
        '.ts', '.tsx', '.json', '.xml', '.svg', '.vue', '.php', '.asp',
        '.aspx', '.jsp',
        
        # Programming languages
        '.py', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.rb', '.go',
        '.rs', '.swift', '.kt', '.kts', '.scala', '.pl', '.pm', '.t',
        '.sh', '.bash', '.ps1', '.psm1', '.r', '.m', '.mm', '.sql',
        '.lua', '.tcl', '.groovy',
        
        # Configuration and data
        '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf', '.properties',
        '.env', '.example', '.template', '.lock', '.dockerfile',
        '.dockerignore',
        
        # Documentation and text
        '.md', '.markdown', '.rst', '.txt', '.text', '.asciidoc', '.adoc',
        '.textile', '.rdoc', '.pod', '.wiki', '.org', '.log',
        
        # Other development files
        '.gitignore', '.dirignore', '.eslintrc', '.prettierrc', '.babelrc',
        '.editorconfig', '.htaccess', '.nginx', '.csv', '.tsv'
    }

def is_vcs_directory(path: Path) -> bool:
    """Check if a path is a VCS directory or inside one."""
    vcs_dirs = get_vcs_directories()
    # Check if any part of the path is a VCS directory
    return any(part.name in vcs_dirs for part in path.parents) or path.name in vcs_dirs

def is_binary_file(file_path: Path) -> bool:
    """
    Determine if a file is binary.
    First checks extension, then examines content if needed.
    """
    # Skip VCS directories entirely
    if is_vcs_directory(file_path):
        return True
        
    # If it's a known text extension, it's not binary
    if file_path.suffix.lower() in get_text_file_extensions():
        return False
        
    try:
        # Read the first chunk of the file
        chunk_size = 8192
        with open(file_path, 'rb') as f:
            chunk = f.read(chunk_size)
            
        # Empty files are considered text
        if not chunk:
            return False
            
        # Check for common binary file signatures
        if chunk.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG signature
            return True
        if chunk.startswith(b'GIF87a') or chunk.startswith(b'GIF89a'):  # GIF
            return True
        if chunk.startswith(b'\xFF\xD8'):  # JPEG
            return True
        if chunk.startswith(b'PK\x03\x04'):  # ZIP and derivatives
            return True
            
        # Count null bytes and other control characters
        null_count = chunk.count(b'\x00')
        control_chars = sum(1 for b in chunk if b < 32 and b not in (9, 10, 13))  # tab, LF, CR
        
        # If we have nulls or too many control chars, it's binary
        if null_count > 0 or (control_chars / len(chunk)) > 0.3:
            return True
            
        return False
            
    except Exception as e:
        print(f"Warning: Error checking if file is binary {file_path}: {e}")
        return True

def get_file_content(file_path: Path) -> Optional[str]:
    """Get content of a text file."""
    # Skip VCS directories entirely
    if is_vcs_directory(file_path):
        return None
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content
    except Exception as e:
        print(f"Warning: Error reading file {file_path}: {e}")
        return None

def read_target_patterns(target_file: str) -> List[str]:
    """Read patterns from a target file (like .dirtarget)."""
    patterns = []
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            patterns = [
                line.strip()
                for line in f
                if line.strip() and not line.strip().startswith('#')
            ]
    except Exception as e:
        print(f"Warning: Error reading target file {target_file}: {e}")
    return patterns