# tests/test_utils.py
from pathlib import Path
import shutil

TEST_DATA_DIR = Path("tests/test_data")

def create_test_directory(debug: bool = False):
    """Create the test directory structure programmatically."""
    if TEST_DATA_DIR.exists():
        if debug:
            print("Test directory already exists, skipping creation")
        return

    # Clean up any existing directory
    shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)
    
    # Create base directories
    dirs = [
        TEST_DATA_DIR / "src/submodule",
        TEST_DATA_DIR / "docs",
        TEST_DATA_DIR / "tests",
        TEST_DATA_DIR / ".git/objects/4e",
        TEST_DATA_DIR / ".git/refs/heads",
        TEST_DATA_DIR / ".git/refs/tags",
        TEST_DATA_DIR / ".git/hooks",
        TEST_DATA_DIR / ".git/info",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Create .git files
    write_text(TEST_DATA_DIR / ".git/HEAD", "ref: refs/heads/main")
    write_text(TEST_DATA_DIR / ".git/config", """[core]
    repositoryformatversion = 0
    filemode = false
    bare = false
    logallrefupdates = true
[remote "origin"]
    url = https://github.com/username/dircontextgen.git
    fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
    remote = origin
    merge = refs/heads/main""")
    write_text(TEST_DATA_DIR / ".git/description", 
              "Unnamed repository; edit this file 'description' to name the repository.")
    write_text(TEST_DATA_DIR / ".git/info/exclude", """# git ls-files --others --exclude-from=.git/info/exclude
# Lines that start with '#' are comments.
# For a project mostly in C, the following would be a good set of
# exclude patterns (uncomment them if you want to use them):
# *.[oa]
# *~""")
    write_text(TEST_DATA_DIR / ".git/packed-refs", """# pack-refs with: peeled fully-peeled sorted 
refs/remotes/origin/main 4e1243bd22c66e76c2ba9eddc1f91394e57f9f83""")
    write_text(TEST_DATA_DIR / ".git/objects/4e/1243bd22c66e76c2ba9eddc1f91394e57f9f83", "x" * 100)

    # Create project files
    write_text(TEST_DATA_DIR / "README.md", "# Test Project\nThis is a test project.")
    write_text(TEST_DATA_DIR / "setup.py", "from setuptools import setup\nsetup(name='test')")
    write_text(TEST_DATA_DIR / "requirements.txt", "pytest\npytest-cov")
    write_text(TEST_DATA_DIR / ".gitignore", "*.pyc\n__pycache__/\n*.log")
    write_text(TEST_DATA_DIR / ".dirignore", "*.tmp\n*.bak\npackage-lock.json")
    write_text(TEST_DATA_DIR / ".dirtarget", "*.py\n*.md\n*.txt")
    write_text(TEST_DATA_DIR / "src/main.py", "def main():\n    pass")
    write_text(TEST_DATA_DIR / "src/utils.py", "def helper():\n    pass")
    write_text(TEST_DATA_DIR / "tests/test_main.py", "def test_main():\n    pass")
    write_text(TEST_DATA_DIR / "src/submodule/.gitignore", "*.cache")
    
    # Create binary files
    png_bytes = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x44, 0x41, 0x54,
        0x78, 0xDA, 0x63, 0x64, 0x60, 0x60, 0x60, 0x00
    ])
    write_binary(TEST_DATA_DIR / "docs/image.png", png_bytes)
    
    # Create large text file
    large_content = "x" * 1048677
    write_text(TEST_DATA_DIR / "docs/large.txt", large_content)
    
    # Create package-lock.json
    write_text(TEST_DATA_DIR / "package-lock.json", """{
  "name": "test-project",
  "version": "1.0.0",
  "lockfileVersion": 2,
  "dependencies": {
    "test-dep": {
      "version": "1.0.0"
    }
  }
}""")

def write_text(path: Path, content: str):
    """Write text content to a file with proper UTF-8 encoding."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def write_binary(path: Path, content: bytes):
    """Write binary content to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)

def cleanup_test_directory():
    """Clean up the test directory."""
    shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)