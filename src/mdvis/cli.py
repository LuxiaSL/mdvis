"""
Enhanced command line interface for mdvis.

Provides a comprehensive, user-friendly CLI with excellent help text,
error handling, and development workflow support.
"""

import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax

from .config.manager import ConfigManager, ConfigurationError
from .config.schema import MDVisConfig

console = Console()


class MDVisError(Exception):
    """Base exception for MDVis CLI errors."""
    pass


def validate_source_path(ctx, param, value):
    """Validate that source path exists and contains Python files."""
    if value is None:
        return None
    
    path = Path(value)
    if not path.exists():
        raise click.BadParameter(f"Source path does not exist: {path}")
    
    if not path.is_dir():
        raise click.BadParameter(f"Source path must be a directory: {path}")
    
    # Check if directory contains Python files
    python_files = list(path.rglob("*.py"))
    if not python_files:
        console.print(f"[yellow]Warning:[/yellow] No Python files found in {path}")
    
    return path


def validate_output_path(ctx, param, value):
    """Validate and prepare output path."""
    if value is None:
        return None
    
    path = Path(value)
    
    # Check if parent directory is writable
    parent = path.parent
    if parent.exists() and not parent.is_dir():
        raise click.BadParameter(f"Output parent path is not a directory: {parent}")
    
    # Create parent directories if they don't exist
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise click.BadParameter(f"Cannot create output directory (permission denied): {parent}")
    
    return path


def validate_config_path(ctx, param, value):
    """Validate configuration file path."""
    if value is None:
        return None
    
    path = Path(value)
    if not path.exists():
        raise click.BadParameter(f"Configuration file does not exist: {path}")
    
    if not path.is_file():
        raise click.BadParameter(f"Configuration path is not a file: {path}")
    
    # Check if it's a YAML file
    if path.suffix.lower() not in {'.yaml', '.yml'}:
        console.print(f"[yellow]Warning:[/yellow] Configuration file should have .yaml or .yml extension")
    
    return path


@click.group(invoke_without_command=True)
@click.version_option(version="0.3.0", prog_name="mdvis")
@click.option('--verbose', '-v', count=True, help="Increase verbosity (-v, -vv, -vvv)")
@click.pass_context
def cli(ctx, verbose):
    """
    MDVis - Python Codebase Documentation Generator
    
    Transform your Python codebases into rich, navigable Obsidian-compatible 
    documentation with smart cross-references, type information, and dependency 
    visualizations.
    
    \b
    Features:
    • Smart cross-references between modules, classes, and functions
    • Type-aware linking that connects type hints to definitions
    • Dependency visualization with Mermaid diagrams
    • Multiple verbosity levels (minimal, standard, detailed)
    • Async pattern detection and event system mapping
    • Highly configurable with multi-layer configuration
    
    \b
    Quick Start:
    • mdvis scan ./src                    # Basic documentation generation
    • mdvis init --project-name "MyApp"   # Create configuration file
    • mdvis scan ./src --verbosity detailed --output ./docs
    
    \b
    Get Help:
    • mdvis COMMAND --help               # Help for specific commands
    • mdvis scan --help                  # Detailed scan options
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    # If no command is provided, show help
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


@cli.command()
@click.argument('source_path', type=click.Path(exists=True, path_type=Path), 
                callback=validate_source_path)
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              callback=validate_output_path,
              help="📁 Output directory for generated documentation")
@click.option('--config', '-c', type=click.Path(exists=True, path_type=Path), 
              callback=validate_config_path,
              help="⚙️  Configuration file path (.yaml/.yml)")
@click.option('--verbosity', type=click.Choice(['minimal', 'standard', 'detailed']),
              help="📖 Documentation detail level")
@click.option('--include-private/--no-private', default=None,
              help="🔒 Include/exclude private methods and classes (_private)")
@click.option('--events/--no-events', default=None,
              help="📡 Enable/disable event detection and documentation")
@click.option('--diagrams/--no-diagrams', default=None,
              help="📊 Enable/disable dependency diagram generation")
@click.option('--auto-format/--no-auto-format', default=None,
              help="🎨 Enable/disable automatic code formatting with autopep8")
@click.option('--exclude', multiple=True, metavar='PATTERN',
              help="🚫 Exclude patterns (glob-style, can be used multiple times)")
@click.option('--watch', '-w', is_flag=True,
              help="👀 Watch for file changes and regenerate documentation")
@click.option('--dry-run', is_flag=True,
              help="🔍 Show what would be processed without generating output")
@click.option('--stats', is_flag=True,
              help="📈 Show detailed processing statistics")
@click.pass_context
async def scan(ctx, source_path, output, config, verbosity, include_private, events, 
         diagrams, auto_format, exclude, watch, dry_run, stats):
    """
    🔍 Scan source code and generate documentation.
    
    SOURCE_PATH is the root directory containing Python source code to document.
    
    \b
    Examples:
    
      Basic usage:
      mdvis scan ./src
      
      Detailed documentation with custom output:
      mdvis scan ./src --output ./docs --verbosity detailed
      
      Use custom config and exclude test files:
      mdvis scan ./src --config ./my-config.yaml --exclude "**/test_*.py"
      
      Include private methods with diagrams:
      mdvis scan ./src --include-private --diagrams
      
      Watch mode for development:
      mdvis scan ./src --output ./docs --watch
      
      Dry run to preview what will be processed:
      mdvis scan ./src --dry-run --stats
    
    \b
    Verbosity Levels:
    • minimal   - Clean headers, basic cross-references
    • standard  - Balanced detail with type information (default)
    • detailed  - Complete metrics, full cross-reference anchors
    
    \b
    Output Structure:
    • Mirror mode (default) - Mirrors source directory structure
    • Generated files use .md extension optimized for Obsidian
    • Includes README.md with project overview and navigation
    """
    try:
        # Enhanced startup message
        _show_startup_banner(source_path, dry_run)
        
        # Build CLI arguments dict for config manager
        cli_args = {}
        if verbosity:
            cli_args['verbosity'] = verbosity
        if include_private is not None:
            cli_args['include_private'] = include_private
        if events is not None:
            cli_args['no_events'] = not events
        if diagrams is not None:
            cli_args['generate_diagrams'] = diagrams
        if auto_format is not None:
            cli_args['auto_format'] = auto_format
        if exclude:
            cli_args['exclude_patterns'] = list(exclude)
        
        # Load and validate configuration
        config_manager = ConfigManager()
        
        with console.status("[bold blue]Loading configuration..."):
            mdvis_config = config_manager.load_config(
                project_root=source_path,
                config_file=config,
                cli_args=cli_args
            )
        
        # Validate configuration with detailed feedback
        validation_errors = config_manager.validate_paths(source_path)
        if validation_errors:
            _show_validation_errors(validation_errors)
            sys.exit(1)
        
        # Determine output path with smart defaults
        if output:
            output_path = output
        else:
            output_path = source_path / 'docs'
            if not dry_run:
                output_path.mkdir(parents=True, exist_ok=True)
        
        # Show configuration info in verbose mode
        if ctx.obj['verbose'] > 0:
            _show_config_info(config_manager, source_path, output_path, mdvis_config)
        
        # Handle dry run
        if dry_run:
            await _show_dry_run_info(mdvis_config, source_path, output_path, stats)
            return
        
        # Handle watch mode
        if watch:
            await _run_watch_mode(mdvis_config, source_path, output_path)
        else:
            # Run single generation
            await _run_generation(mdvis_config, source_path, output_path, stats)
        
    except ConfigurationError as e:
        _show_error("Configuration Error", str(e), "Check your configuration file syntax and paths")
        sys.exit(1)
    except FileNotFoundError as e:
        _show_error("File Not Found", str(e), "Ensure all specified paths exist")
        sys.exit(1)
    except PermissionError as e:
        _show_error("Permission Error", str(e), "Check file/directory permissions")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]⏹️  Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        _show_error("Unexpected Error", str(e))
        if ctx.obj['verbose'] > 1:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option('--project-name', '-n', help="📝 Project name for the configuration")
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              default=Path('docs/mdvis.yaml'), 
              help="📄 Output path for configuration file")
@click.option('--user', is_flag=True, help="👤 Create user-level config instead of project config")
@click.option('--template', type=click.Choice(['minimal', 'standard', 'comprehensive']),
              default='standard', help="📋 Configuration template to use")
def init(project_name, output, user, template):
    """
    ⚙️  Create a default configuration file.
    
    This generates a commented configuration file with sensible defaults
    that you can customize for your project.
    
    \b
    📋 Examples:
    
      Create project config:
      mdvis init --project-name "MyProject"
      
      Create comprehensive config with all options:
      mdvis init --project-name "MyApp" --template comprehensive
      
      Create user-level config:
      mdvis init --user
      
      Custom output location:
      mdvis init --output ./config/mdvis.yaml
    
    \b
    📁 Config Locations:
    • Project: ./docs/mdvis.yaml (committed with project)
    • User: ~/.config/mdvis/config.yaml (personal defaults)
    """
    try:
        config_manager = ConfigManager()
        
        if user:
            # Create user config
            from os import environ
            config_dir = Path(environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
            output_path = config_dir / 'mdvis' / 'config.yaml'
            console.print(f"[dim]Creating user configuration at {output_path}[/dim]")
        else:
            output_path = output
            console.print(f"[dim]Creating project configuration at {output_path}[/dim]")
        
        if output_path.exists():
            if not click.confirm(f"Config file {output_path} already exists. Overwrite?"):
                console.print("[yellow]⏹️  Operation cancelled[/yellow]")
                return
        
        with console.status("[bold blue]Creating configuration file..."):
            config_manager.create_default_config_file(output_path, project_name)
        
        # Success message with next steps
        console.print(Panel(
            f"[green]✅ Configuration file created successfully![/green]\n\n"
            f"📄 Location: {output_path}\n"
            f"📝 Template: {template}\n\n"
            f"[dim]Next steps:[/dim]\n"
            f"1. Edit the configuration file to customize settings\n"
            f"2. Run: [bold]mdvis scan ./src[/bold] to generate documentation\n"
            f"3. Use: [bold]mdvis validate[/bold] to check your configuration",
            title="🎉 Setup Complete",
            expand=False
        ))
        
    except Exception as e:
        _show_error("Configuration Creation Failed", str(e))
        sys.exit(1)


@cli.command()
@click.argument('config_path', type=click.Path(exists=True, path_type=Path), 
                callback=validate_config_path, required=False)
@click.option('--source', type=click.Path(exists=True, path_type=Path), 
              callback=validate_source_path,
              help="📁 Source directory to validate against")
@click.option('--detailed', is_flag=True, help="📊 Show detailed validation information")
def validate(config_path, source, detailed):
    """
    ✅ Validate configuration file and project setup.
    
    Checks configuration syntax, validates paths, and reports any issues.
    Helps ensure your setup is correct before running documentation generation.
    
    CONFIG_PATH is the path to the configuration file to validate.
    If not provided, searches for config in standard locations.
    
    \b
    📋 Examples:
    
      Validate current project configuration:
      mdvis validate
      
      Validate specific config file:
      mdvis validate ./my-config.yaml
      
      Validate with detailed information:
      mdvis validate --detailed
      
      Validate against specific source directory:
      mdvis validate --source ./src
    """
    try:
        config_manager = ConfigManager()
        
        # Determine source path
        source_path = source or Path.cwd()
        
        with console.status("[bold blue]Loading and validating configuration..."):
            # Load configuration
            mdvis_config = config_manager.load_config(
                project_root=source_path,
                config_file=config_path
            )
            
            # Validate configuration
            validation_errors = config_manager.validate_paths(source_path)
        
        if validation_errors:
            _show_validation_errors(validation_errors)
            sys.exit(1)
        else:
            console.print("[green]✅ Configuration is valid![/green]")
            
            if detailed:
                _show_detailed_config_info(config_manager, mdvis_config, source_path)
        
    except ConfigurationError as e:
        _show_error("Configuration Error", str(e))
        sys.exit(1)
    except Exception as e:
        _show_error("Validation Error", str(e))
        sys.exit(1)


@cli.command()
@click.argument('output_path', type=click.Path(path_type=Path), callback=validate_output_path)
@click.option('--force', '-f', is_flag=True, help="🗑️  Remove files without confirmation")
@click.option('--backup', is_flag=True, help="💾 Create backup before cleaning")
def clean(output_path, force, backup):
    """
    Remove generated documentation files.
    
    OUTPUT_PATH is the documentation directory to clean.
    
    This removes all .md files and other generated content from the
    specified directory, helping you start fresh.
    
    \b
    Examples:
    
      Clean documentation directory:
      mdvis clean ./docs
      
      Force clean without confirmation:
      mdvis clean ./docs --force
      
      Clean with backup:
      mdvis clean ./docs --backup
    
    \b
    Safety:
    • Only removes .md files and known generated content
    • Preserves your custom documentation files
    • Use --backup for extra safety
    """
    try:
        if not output_path.exists():
            console.print(f"[yellow]📁 Directory does not exist:[/yellow] {output_path}")
            return
        
        # Find generated files
        md_files = list(output_path.rglob('*.md'))
        processing_files = list(output_path.rglob('_processing_status.md'))
        
        all_files = md_files + processing_files
        
        if not all_files:
            console.print(f"[yellow]📄 No documentation files found in:[/yellow] {output_path}")
            return
        
        # Show what will be removed
        console.print(f"[bold]Found {len(all_files)} files to remove:[/bold]")
        for file in all_files[:10]:  # Show first 10
            console.print(f"  📄 {file.relative_to(output_path)}")
        if len(all_files) > 10:
            console.print(f"  📄 ... and {len(all_files) - 10} more files")
        
        # Create backup if requested
        if backup:
            backup_path = output_path.parent / f"{output_path.name}_backup_{int(time.time())}"
            console.print(f"[dim]Creating backup at: {backup_path}[/dim]")
            # TODO: Implement backup functionality
        
        # Confirm removal
        if not force:
            if not click.confirm(f"\n🗑️  Remove {len(all_files)} files from {output_path}?"):
                console.print("[yellow]⏹️  Operation cancelled[/yellow]")
                return
        
        # Remove files with progress
        with Progress() as progress:
            task = progress.add_task("🗑️  Cleaning files...", total=len(all_files))
            
            removed_count = 0
            for file in all_files:
                try:
                    file.unlink()
                    removed_count += 1
                except Exception as e:
                    console.print(f"[red]❌ Error removing {file}:[/red] {e}")
                progress.advance(task)
        
        console.print(f"[green]✅ Removed {removed_count} documentation files[/green]")
        
    except Exception as e:
        _show_error("Clean Operation Failed", str(e))
        sys.exit(1)


@cli.command()
@click.argument('source_path', type=click.Path(exists=True, path_type=Path), 
                callback=validate_source_path)
def stats(source_path):
    """
    📊 Show statistics about a Python codebase.
    
    Analyzes the codebase and provides detailed statistics about
    files, classes, functions, and complexity without generating
    documentation.
    
    SOURCE_PATH is the root directory containing Python source code.
    
    \b
    📋 Examples:
    
      Show codebase statistics:
      mdvis stats ./src
      
      Analyze current directory:
      mdvis stats .
    """
    try:
        from .core.scanner import get_file_stats
        
        with console.status("[bold blue]Analyzing codebase..."):
            file_stats = asyncio.run(get_file_stats([source_path]))
        
        _show_codebase_stats(file_stats, source_path)
        
    except Exception as e:
        _show_error("Statistics Analysis Failed", str(e))
        sys.exit(1)


# Helper functions for enhanced UI

def _show_startup_banner(source_path: Path, dry_run: bool = False):
    """Show enhanced startup banner."""
    mode = "🔍 DRY RUN" if dry_run else "🚀 GENERATING"
    
    banner = Panel(
        f"[bold blue]{mode} - MDVis Documentation Generator[/bold blue]\n\n"
        f"📁 Source: {source_path}\n"
        f"🕒 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        title="🎯 MDVis",
        expand=False
    )
    console.print(banner)


def _show_error(title: str, message: str, suggestion: str = None):
    """Show formatted error message."""
    error_text = f"[red]❌ {message}[/red]"
    if suggestion:
        error_text += f"\n\n[dim]💡 Suggestion: {suggestion}[/dim]"
    
    console.print(Panel(error_text, title=f"[red]{title}[/red]", expand=False))


def _show_validation_errors(errors: List[str]):
    """Show formatted validation errors."""
    error_text = "[red]Configuration validation failed:[/red]\n\n"
    for i, error in enumerate(errors, 1):
        error_text += f"{i}. {error}\n"
    
    error_text += "\n[dim]💡 Fix these issues and try again[/dim]"
    
    console.print(Panel(error_text, title="[red]❌ Validation Errors[/red]", expand=False))


def _show_config_info(config_manager: ConfigManager, source_path: Path, 
                     output_path: Path, config: MDVisConfig):
    """Show enhanced configuration information."""
    config_info = config_manager.get_config_info()
    
    table = Table(title="⚙️ Configuration Details", show_header=True)
    table.add_column("Setting", style="cyan", width=20)
    table.add_column("Value", style="green")
    
    table.add_row("Source Path", str(source_path))
    table.add_row("Output Path", str(output_path))
    table.add_row("Verbosity", config.verbosity)
    table.add_row("Include Private", str(config.output.include_private))
    table.add_row("Events Enabled", str(config.events.enabled))
    table.add_row("Generate Diagrams", str(config.visualization.generate_dependency_graph))
    
    if config_info['project_config_path']:
        table.add_row("Project Config", config_info['project_config_path'])
    if config_info['user_config_path']:
        table.add_row("User Config", config_info['user_config_path'])
    
    console.print(table)


def _show_detailed_config_info(config_manager: ConfigManager, config: MDVisConfig, source_path: Path):
    """Show detailed configuration validation info."""
    config_info = config_manager.get_config_info()
    
    # Configuration summary table
    table = Table(title="📋 Configuration Summary")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Verbosity", config.verbosity)
    table.add_row("Events Enabled", str(config.events.enabled))
    table.add_row("Include Private", str(config.output.include_private))
    table.add_row("Source Paths", ", ".join(config.project.source_paths))
    table.add_row("Auto Format", str(config.linting.auto_format))
    table.add_row("Generate Diagrams", str(config.visualization.generate_dependency_graph))
    
    console.print(table)
    
    # Configuration sources
    if config_info['project_config_path'] or config_info['user_config_path']:
        console.print("\n[bold]📁 Configuration Sources:[/bold]")
        if config_info['project_config_path']:
            console.print(f"  📄 Project: {config_info['project_config_path']}")
        if config_info['user_config_path']:
            console.print(f"  👤 User: {config_info['user_config_path']}")
        if config_info['cli_overrides']:
            console.print(f"  ⚡ CLI Overrides: {', '.join(config_info['cli_overrides'].keys())}")


async def _show_dry_run_info(config: MDVisConfig, source_path: Path, 
                           output_path: Path, show_stats: bool = False):
    """Show enhanced dry run information."""
    console.print(Panel(
        f"[bold yellow]🔍 DRY RUN - Preview Mode[/bold yellow]\n\n"
        f"This shows what would be processed without generating output.\n"
        f"Use without --dry-run to actually generate documentation.",
        title="ℹ️  Preview Mode",
        expand=False
    ))
    
    # Configuration preview
    table = Table(title="📋 Processing Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Source Directory", str(source_path))
    table.add_row("Output Directory", str(output_path))
    table.add_row("Verbosity Level", config.verbosity)
    table.add_row("Include Private", str(config.output.include_private))
    table.add_row("Event Detection", str(config.events.enabled))
    table.add_row("Generate Diagrams", str(config.visualization.generate_dependency_graph))
    
    console.print(table)
    
    # Source paths validation
    console.print("\n[bold]📁 Source Paths:[/bold]")
    for source in config.project.source_paths:
        path = source_path / source
        status = "✅" if path.exists() else "❌"
        console.print(f"  {status} {source}")
    
    # Exclusion patterns
    if config.project.exclude_patterns:
        console.print("\n[bold]🚫 Exclude Patterns:[/bold]")
        for pattern in config.project.exclude_patterns:
            console.print(f"  • {pattern}")
    
    # File statistics if requested
    if show_stats:
        from .core.scanner import get_file_stats
        
        with console.status("[bold blue]Analyzing files..."):
            file_stats = await get_file_stats([source_path], config.project.exclude_patterns)
        
        console.print("\n[bold]📊 File Statistics:[/bold]")
        console.print(f"  📄 Total files: {file_stats['total_files']}")
        console.print(f"  📝 Total lines: {file_stats['total_lines']:,}")
        console.print(f"  📦 Average file size: {file_stats['average_file_size']:.1f} bytes")
        console.print(f"  📏 Average lines per file: {file_stats['average_lines_per_file']:.1f}")


def _show_codebase_stats(stats: dict, source_path: Path):
    """Show detailed codebase statistics."""
    console.print(Panel(
        f"[bold blue]📊 Codebase Analysis Results[/bold blue]\n\n"
        f"📁 Source: {source_path}",
        title="📈 Statistics",
        expand=False
    ))
    
    # Main statistics table
    table = Table(title="📋 Overview")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green", justify="right")
    
    table.add_row("Total Files", f"{stats['total_files']:,}")
    table.add_row("Total Lines", f"{stats['total_lines']:,}")
    table.add_row("Total Size", f"{stats['total_size_bytes']:,} bytes")
    table.add_row("Average File Size", f"{stats['average_file_size']:.1f} bytes")
    table.add_row("Average Lines/File", f"{stats['average_lines_per_file']:.1f}")
    table.add_row("Readable Files", f"{stats['readable_files']}")
    
    console.print(table)
    
    # Encoding distribution
    if stats['encoding_distribution']:
        console.print("\n[bold]📝 File Encodings:[/bold]")
        for encoding, count in stats['encoding_distribution'].items():
            console.print(f"  • {encoding}: {count} files")


async def _run_generation(config: MDVisConfig, source_path: Path, output_path: Path, show_stats: bool = False):
    """Run enhanced documentation generation with better progress reporting."""
    from .core.processor import DocumentationProcessor
    
    processor = DocumentationProcessor(config)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        
        main_task = progress.add_task("🚀 Starting documentation generation...", total=100)
        
        try:
            # Phase tracking
            progress.update(main_task, description="📁 Discovering files...", completed=10)
            await processor._phase_discovery(source_path)
            
            progress.update(main_task, description="📜 Parsing source code...", completed=30)
            await processor._phase_parsing()
            
            progress.update(main_task, description="🔗 Building cross-references...", completed=50)
            await processor._phase_indexing()
            
            progress.update(main_task, description="🧠 Enhanced analysis...", completed=70)
            await processor._phase_analysis()
            
            progress.update(main_task, description="📝 Generating documentation...", completed=90)
            await processor._phase_generation(output_path)
            
            progress.update(main_task, description="✅ Documentation generated!", completed=100)
            
        except Exception as e:
            progress.update(main_task, description=f"❌ Generation failed: {e}")
            raise
    
    # Success message with results
    summary = processor.get_processing_summary()
    
    console.print(Panel(
        f"[green]✅ Documentation generated successfully![/green]\n\n"
        f"📊 Processed {summary['stats']['modules_created']} modules\n"
        f"🏗️  Found {summary['stats']['classes_found']} classes\n"
        f"⚡ Found {summary['stats']['functions_found']} functions\n"
        f"🔗 Resolved {summary['stats']['imports_resolved']} imports\n"
        f"📁 Output: {output_path}\n\n"
        f"[dim]💡 Open {output_path}/README.md in Obsidian to start exploring![/dim]",
        title="🎉 Generation Complete",
        expand=False
    ))
    
    # Show detailed stats if requested
    if show_stats:
        _show_generation_stats(summary)


def _show_generation_stats(summary: dict):
    """Show detailed generation statistics."""
    stats = summary['stats']
    
    table = Table(title="📊 Detailed Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green", justify="right")
    
    table.add_row("Files Discovered", f"{stats['files_discovered']}")
    table.add_row("Files Processed", f"{stats['files_processed']}")
    table.add_row("Files Failed", f"{stats['files_failed']}")
    table.add_row("Total Lines", f"{stats['total_lines']:,}")
    table.add_row("Processing Time", f"{stats['processing_time']:.2f}s")
    table.add_row("Cross-references", f"{stats['cross_references']}")
    
    console.print(table)
    
    # Show errors if any
    if summary.get('errors'):
        console.print("\n[bold]⚠️  Errors encountered:[/bold]")
        for error in summary['errors'][:5]:  # Show first 5
            console.print(f"  • {error}")
        if len(summary['errors']) > 5:
            console.print(f"  • ... and {len(summary['errors']) - 5} more")


async def _run_watch_mode(config: MDVisConfig, source_path: Path, output_path: Path):
    """Enhanced watch mode (placeholder for future implementation)."""
    console.print(Panel(
        f"[yellow]🚧 Watch mode is not yet implemented[/yellow]\n\n"
        f"This feature will monitor {source_path} for changes and\n"
        f"automatically regenerate documentation in {output_path}.\n\n"
        f"[dim]💡 For now, use regular scan mode and re-run when needed.[/dim]",
        title="⏰ Coming Soon",
        expand=False
    ))


def main():
    """Enhanced main entry point."""
    try:
        cli()
    except Exception as e:
        console.print(f"[red]💥 Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()