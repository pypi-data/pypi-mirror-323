# tests/test_core.py
import pytest
from pathlib import Path
from dircontextgen.core import DocumentationGenerator

def test_documentation_generator_init():
    """Test DocumentationGenerator initialization."""
    generator = DocumentationGenerator(".")
    assert generator.base_dir == Path(".")
    assert generator.tree_only is False
    assert generator.max_file_size == 1024*1024

def test_documentation_generator_custom_init():
    """Test DocumentationGenerator initialization with custom values."""
    generator = DocumentationGenerator(
        ".",
        output_file="custom.txt",
        additional_ignore_files=[".customignore"],
        target_file=".customtarget",
        tree_only=True,
        max_file_size=500000,
        exclude_patterns=["*.tmp"],
        include_patterns=["*.py"],
        verbose=True
    )
    assert generator.output_file == Path("custom.txt")
    assert generator.additional_ignore_files == [".customignore"]
    assert generator.target_file == ".customtarget"
    assert generator.tree_only is True
    assert generator.max_file_size == 500000
    assert generator.exclude_patterns == ["*.tmp"]
    assert generator.include_patterns == ["*.py"]
    assert generator.verbose is True

def test_vcs_handling(temp_project):
    """Test VCS directory handling using temporary directory."""
    # Create VCS directories and files
    vcs_dir = temp_project / '.git'
    vcs_dir.mkdir()
    vcs_file = vcs_dir / 'config'
    vcs_file.write_text("VCS config content")
    
    nested_vcs = temp_project / 'src' / '.svn'
    nested_vcs.mkdir(parents=True)
    nested_file = nested_vcs / 'entries'
    nested_file.write_text("SVN entries")
    
    # Create normal file
    normal_file = temp_project / 'src' / 'main.py'
    normal_file.write_text("print('hello')")
    
    generator = DocumentationGenerator(str(temp_project))
    
    # Test file inclusion logic
    assert generator._should_include_file(vcs_file) is False
    assert generator._should_include_file(nested_file) is False
    assert generator._should_include_file(normal_file) is True

def test_existing_structure(test_data_dir):
    """Test using the programmatically created test directory."""
    # Verify directory structure
    assert (test_data_dir / "src/main.py").exists()
    assert (test_data_dir / "docs/image.png").exists()
    assert (test_data_dir / ".git/HEAD").exists()
    
    # Verify file contents
    gitignore_content = (test_data_dir / ".gitignore").read_text()
    assert "*.pyc" in gitignore_content
    assert "__pycache__/" in gitignore_content
    
    dirtarget_content = (test_data_dir / ".dirtarget").read_text()
    assert "*.py" in dirtarget_content
    assert "*.md" in dirtarget_content
    
    # Verify binary file
    png_file = test_data_dir / "docs/image.png"
    assert png_file.stat().st_size == 24
    
    # Verify large file
    large_file = test_data_dir / "docs/large.txt"
    assert large_file.stat().st_size > 1024*1024  # Over 1MB

def test_load_patterns(test_data_dir):
    """Test pattern loading from various sources."""
    generator = DocumentationGenerator(
        str(test_data_dir),
        additional_ignore_files=[".dirignore"],
        target_file=str(test_data_dir / ".dirtarget")
    )
    generator._load_patterns()
    
    # Check patterns
    base_dir_str = str(test_data_dir.resolve())
    assert base_dir_str in generator.ignore_patterns
    patterns = generator.ignore_patterns[base_dir_str]
    assert "*.pyc" in patterns
    assert "*.tmp" in patterns
    assert "*.py" in generator.target_patterns

def test_should_include_file(test_data_dir):
    """Test file inclusion logic with pre-generated data."""
    generator = DocumentationGenerator(str(test_data_dir))
    generator._load_patterns()
    
    # Test inclusions
    readme_file = test_data_dir / "README.md"
    assert generator._should_include_file(readme_file) is True
    
    # Test excluded package-lock.json (from .dirignore)
    package_lock = test_data_dir / "package-lock.json"
    assert generator._should_include_file(package_lock) is False

def test_generate_documentation(test_data_dir, tmp_path):
    """Test full documentation generation with pre-built data."""
    output_file = tmp_path / "output.txt"
    generator = DocumentationGenerator(
        str(test_data_dir),
        output_file=str(output_file),
        verbose=True
    )
    generator.generate()

    content = output_file.read_text()

    # Split content into directory structure and file contents
    parts = content.split("File Contents\n-------------\n")
    dir_structure = parts[0]
    file_contents = parts[1] if len(parts) > 1 else ''

    # Verify ignored file in directory structure
    assert "package-lock.json" not in dir_structure, (
        f"package-lock.json found in directory structure:\n{dir_structure}"
    )

    # Verify ignored file content is not included
    assert "File: package-lock.json" not in file_contents, (
        f"package-lock.json content included:\n{file_contents}"
    )

def test_large_file_handling(test_data_dir):
    """Test that large files are skipped."""
    large_file = test_data_dir / "docs/large.txt"
    generator = DocumentationGenerator(str(test_data_dir))
    
    # File should be included in structure but not content
    assert generator._should_include_file(large_file) is True
    assert generator._should_include_content(large_file) is False

def test_binary_file_handling(test_data_dir):
    """Test that binary files are excluded from content."""
    png_file = test_data_dir / "docs/image.png"
    generator = DocumentationGenerator(str(test_data_dir))

    # Should be included in structure but excluded from content
    assert generator._should_include_file(png_file) is True  # Included in structure
    assert generator._should_include_content(png_file) is False  # Excluded from content