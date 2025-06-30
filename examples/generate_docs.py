#!/usr/bin/env python3
"""
Example script showing how to use mdvis programmatically.

This demonstrates the main API for generating documentation
without using the command line interface.
"""

import asyncio
from pathlib import Path

from mdvis import MDVisConfig, ConfigManager, DocumentationProcessor


async def generate_documentation_example():
    """Example of generating documentation programmatically."""
    
    # Method 1: Use default configuration
    print("=== Method 1: Default Configuration ===")
    
    config = MDVisConfig()  # Uses built-in defaults
    processor = DocumentationProcessor(config)
    
    source_path = Path("./src")
    output_path = Path("./docs")
    
    if source_path.exists():
        await processor.process_codebase(source_path, output_path)
        summary = processor.get_processing_summary()
        print(f"Processed {summary['stats']['modules_created']} modules")
        print(f"Found {summary['stats']['classes_found']} classes")
        print(f"Found {summary['stats']['functions_found']} functions")
    else:
        print(f"Source path {source_path} does not exist")
    
    print()
    
    # Method 2: Use configuration manager with custom settings
    print("=== Method 2: Custom Configuration ===")
    
    config_manager = ConfigManager()
    
    # Custom CLI-style arguments
    cli_args = {
        'verbosity': 'detailed',
        'include_private': True,
        'generate_diagrams': True
    }
    
    config = config_manager.load_config(
        project_root=Path("."),
        cli_args=cli_args
    )
    
    # Override specific settings
    config.output.include_source = True
    config.output.source_position = "bottom"
    config.events.enabled = True
    
    processor = DocumentationProcessor(config)
    
    if source_path.exists():
        await processor.process_codebase(source_path, output_path)
        
        # Access results
        modules = processor.modules
        index = processor.index
        
        print(f"Generated documentation for {len(modules)} modules")
        if index:
            print(f"Built index with {len(index.functions)} functions")
            print(f"Resolved {len(index.import_resolutions)} imports")
            print(f"Found {len(index.event_flows)} event types")
    
    print()
    
    # Method 3: Configuration from file
    print("=== Method 3: Configuration from File ===")
    
    config_file = Path("./docs/mdvis.yaml")
    if config_file.exists():
        config = config_manager.load_config(
            project_root=Path("."),
            config_file=config_file
        )
        
        processor = DocumentationProcessor(config)
        await processor.process_codebase(source_path, output_path)
        print("Generated documentation using config file")
    else:
        print(f"Config file {config_file} not found")


def create_example_config():
    """Create an example configuration file."""
    
    config_manager = ConfigManager()
    config_path = Path("./examples/example-config.yaml")
    
    # Create the config file
    config_manager.create_default_config_file(
        config_path, 
        project_name="Example Project"
    )
    
    print(f"Created example configuration: {config_path}")


def validate_configuration_example():
    """Example of validating configuration."""
    
    config_manager = ConfigManager()
    
    try:
        config = config_manager.load_config(project_root=Path("."))
        errors = config_manager.validate_paths(Path("."))
        
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("✓ Configuration is valid")
            
            # Show configuration info
            info = config_manager.get_config_info()
            print(f"Effective verbosity: {config.verbosity}")
            print(f"Events enabled: {config.events.enabled}")
            print(f"Source paths: {config.project.source_paths}")
            
    except Exception as e:
        print(f"Configuration error: {e}")


async def main():
    """Main example function."""
    print("MDVis Programmatic API Examples")
    print("=" * 40)
    
    # Create example config
    create_example_config()
    print()
    
    # Validate configuration
    validate_configuration_example()
    print()
    
    # Generate documentation
    await generate_documentation_example()


if __name__ == "__main__":
    asyncio.run(main())