# dircontextgen/cli.py
import click
from pathlib import Path
from typing import List, Optional

@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--output-file', '-o', type=click.Path(), 
              default='project_documentation.txt',
              help='Output file path')
@click.option('--ignore-file', '-i', type=click.Path(exists=True), 
              multiple=True,
              help='Additional ignore file paths')
@click.option('--target-file', '-t', type=click.Path(exists=True),
              help='Target file for explicit inclusion (like .dirtarget)')
@click.option('--tree-only', is_flag=True,
              help='Only show files in tree without contents')
@click.option('--max-file-size', type=click.INT, 
              default=1024*1024,  # 1MB default
              help='Skip files larger than size in bytes')
@click.option('--exclude-pattern', '-e', multiple=True,
              help='Additional patterns to exclude')
@click.option('--include-pattern', '-n', multiple=True,
              help='Patterns to explicitly include')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
@click.option('--show-directory-structure', type=click.Choice(['minimal', 'complete', 'smart'], 
              case_sensitive=False), default='minimal',
              help='Choose how to display directory structure:\n'
                   'minimal: Only show included files (default)\n'
                   'complete: Show all non-VCS files\n'
                   'smart: Show all with collapsed large directories')
@click.option('--collapse-threshold', type=click.INT, default=10,
              help='Number of files before collapsing a directory in smart mode')
def main(directory: str,
         output_file: str,
         ignore_file: tuple,
         target_file: Optional[str],
         tree_only: bool,
         max_file_size: int,
         exclude_pattern: tuple,
         include_pattern: tuple,
         verbose: bool,
         show_directory_structure: str,
         collapse_threshold: int) -> None:
    """Generate documentation from directory contents with advanced filtering.
    
    This tool helps you create context files optimized for AI coding assistants
    by generating a clear view of your project structure and relevant file contents.
    """
    try:
        from .core import DocumentationGenerator
        
        # Initialize generator with CLI options
        generator = DocumentationGenerator(
            base_dir=directory,
            output_file=output_file,
            additional_ignore_files=list(ignore_file),
            target_file=target_file,
            tree_only=tree_only,
            max_file_size=max_file_size,
            exclude_patterns=list(exclude_pattern),
            include_patterns=list(include_pattern),
            verbose=verbose,
            structure_mode=show_directory_structure,
            collapse_threshold=collapse_threshold
        )
        
        # Generate documentation
        generator.generate()
        
        click.echo(f"Documentation generated successfully in {output_file}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()