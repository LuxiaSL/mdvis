# cli

> Enhanced command line interface for mdvis.

Provides a comprehensive, user-friendly CLI with excellent help text,
error handling, and development workflow support.

## Overview

- **Classes:** 1
- **Functions:** 20
- **Lines of Code:** 839

## Imports
- **import** `asyncio`
- **import** `sys`
- **import** `time`
- **from** `datetime` **import** `datetime`
- **from** `pathlib` **import** `Path`
- **from** `typing` **import** `List, Optional, Tuple`
- **import** `click`
- **from** `rich.console` **import** `Console`
- **from** `rich.progress` **import** `Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn`
- **from** `rich.table` **import** `Table`
- **from** `rich.panel` **import** `Panel`
- **from** `rich.text` **import** `Text`
- **from** `rich.syntax` **import** `Syntax`
- **from** `config.manager` **import** `ConfigManager, ConfigurationError`
- **from** `config.schema` **import** `MDVisConfig`

## Classes
### MDVisError {#class-mdviserror}

> Base exception for MDVis CLI errors.

**Inherits from:** `Exception`


## Functions
### validate_source_path {#function-validate-source-path}

> Validate that source path exists and contains Python files.

**Signature:** `def validate_source_path(ctx, param, value)`
### validate_output_path {#function-validate-output-path}

> Validate and prepare output path.

**Signature:** `def validate_output_path(ctx, param, value)`
### validate_config_path {#function-validate-config-path}

> Validate configuration file path.

**Signature:** `def validate_config_path(ctx, param, value)`
### cli {#function-cli}

> MDVis - Python Codebase Documentation Generator

Transform your Python codebases into rich, navigable Obsidian-compatible 
documentation with smart cross-references, type information, and dependency 
visualizations.


Features:
• Smart cross-references between modules, classes, and functions
• Type-aware linking that connects type hints to definitions
• Dependency visualization with Mermaid diagrams
• Multiple verbosity levels (minimal, standard, detailed)
• Async pattern detection and event system mapping
• Highly configurable with multi-layer configuration


Quick Start:
• mdvis scan ./src                    # Basic documentation generation
• mdvis init --project-name "MyApp"   # Create configuration file
• mdvis scan ./src --verbosity detailed --output ./docs


Get Help:
• mdvis COMMAND --help               # Help for specific commands
• mdvis scan --help                  # Detailed scan options

**Signature:** `def cli(ctx, verbose)`
### scan {#function-scan}

> Scan source code and generate documentation.

SOURCE_PATH is the root directory containing Python source code to document.


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


Verbosity Levels:
• minimal   - Clean headers, basic cross-references
• standard  - Balanced detail with type information (default)
• detailed  - Complete metrics, full cross-reference anchors


Output Structure:
• Mirror mode (default) - Mirrors source directory structure
• Generated files use .md extension optimized for Obsidian
• Includes README.md with project overview and navigation

**Signature:** `def scan(ctx, source_path, output, config, verbosity, include_private, events, diagrams, auto_format, exclude, watch, dry_run, stats)`
### init {#function-init}

> Create a default configuration file.

This generates a commented configuration file with sensible defaults
that you can customize for your project.


Examples:

  Create project config:
  mdvis init --project-name "MyProject"
  
  Create comprehensive config with all options:
  mdvis init --project-name "MyApp" --template comprehensive
  
  Create user-level config:
  mdvis init --user
  
  Custom output location:
  mdvis init --output ./config/mdvis.yaml


Config Locations:
• Project: ./docs/mdvis.yaml (committed with project)
• User: ~/.config/mdvis/config.yaml (personal defaults)

**Signature:** `def init(project_name, output, user, template)`
### validate {#function-validate}

> Validate configuration file and project setup.

Checks configuration syntax, validates paths, and reports any issues.
Helps ensure your setup is correct before running documentation generation.

CONFIG_PATH is the path to the configuration file to validate.
If not provided, searches for config in standard locations.


Examples:

  Validate current project configuration:
  mdvis validate
  
  Validate specific config file:
  mdvis validate ./my-config.yaml
  
  Validate with detailed information:
  mdvis validate --detailed
  
  Validate against specific source directory:
  mdvis validate --source ./src

**Signature:** `def validate(config_path, source, detailed)`
### clean {#function-clean}

> Remove generated documentation files.

OUTPUT_PATH is the documentation directory to clean.

This removes all .md files and other generated content from the
specified directory, helping you start fresh.


Examples:

  Clean documentation directory:
  mdvis clean ./docs
  
  Force clean without confirmation:
  mdvis clean ./docs --force
  
  Clean with backup:
  mdvis clean ./docs --backup


Safety:
• Only removes .md files and known generated content
• Preserves your custom documentation files
• Use --backup for extra safety

**Signature:** `def clean(output_path, force, backup)`
### stats {#function-stats}

> Show statistics about a Python codebase.

Analyzes the codebase and provides detailed statistics about
files, classes, functions, and complexity without generating
documentation.

SOURCE_PATH is the root directory containing Python source code.


Examples:

  Show codebase statistics:
  mdvis stats ./src
  
  Analyze current directory:
  mdvis stats .

**Signature:** `def stats(source_path)`
### _show_startup_banner {#function-show-startup-banner}

> Show enhanced startup banner.

**Signature:** `def _show_startup_banner(source_path: Path, dry_run: bool = False)`
### _show_error {#function-show-error}

> Show formatted error message.

**Signature:** `def _show_error(title: str, message: str, suggestion: str = None)`
### _show_validation_errors {#function-show-validation-errors}

> Show formatted validation errors.

**Signature:** `def _show_validation_errors(errors: List[str])`
### _show_config_info {#function-show-config-info}

> Show enhanced configuration information.

**Signature:** `def _show_config_info(config_manager: ConfigManager, source_path: Path, output_path: Path, config: MDVisConfig)`
### _show_detailed_config_info {#function-show-detailed-config-info}

> Show detailed configuration validation info.

**Signature:** `def _show_detailed_config_info(config_manager: ConfigManager, config: MDVisConfig, source_path: Path)`
### _show_dry_run_info {#function-show-dry-run-info}

> Show enhanced dry run information.

**Signature:** `async def _show_dry_run_info(config: MDVisConfig, project_root: Path, output_path: Path, show_stats: bool = False)`
### _show_codebase_stats {#function-show-codebase-stats}

> Show detailed codebase statistics.

**Signature:** `def _show_codebase_stats(stats: dict, source_path: Path)`
### _run_generation {#function-run-generation}

> Run enhanced documentation generation with clean progress reporting.

**Signature:** `async def _run_generation(config: MDVisConfig, project_root: Path, output_path: Path, show_stats: bool = False)`
### _show_generation_stats {#function-show-generation-stats}

> Show detailed generation statistics.

**Signature:** `def _show_generation_stats(summary: dict)`
### _run_watch_mode {#function-run-watch-mode}

> Enhanced watch mode (placeholder for future implementation).

**Signature:** `async def _run_watch_mode(config: MDVisConfig, project_root: Path, output_path: Path)`
### main {#function-main}

> Enhanced main entry point.

**Signature:** `def main()`
