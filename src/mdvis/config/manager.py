"""
Configuration manager with multi-layer resolution.

Handles the priority chain: CLI Args → Project Config → User Config → Built-in Defaults
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import ValidationError

from .schema import MDVisConfig, get_default_config


class ConfigurationError(Exception):
    """Configuration-related error."""
    pass


class ConfigManager:
    """
    Manages configuration loading and resolution with multiple layers.
    
    Priority order (highest to lowest):
    1. CLI arguments (runtime behavior)
    2. Project config file (./docs/mdvis.yaml or specified path)
    3. User config file (~/.config/mdvis/config.yaml)  
    4. Built-in defaults
    """
    
    def __init__(self):
        self._config: Optional[MDVisConfig] = None
        self._cli_overrides: Dict[str, Any] = {}
        self._project_config_path: Optional[Path] = None
        self._user_config_path: Optional[Path] = None
    
    def load_config(
        self,
        project_root: Optional[Path] = None,
        config_file: Optional[Path] = None,
        cli_args: Optional[Dict[str, Any]] = None
    ) -> MDVisConfig:
        """
        Load configuration with multi-layer resolution.
        
        Args:
            project_root: Root directory to search for project config
            config_file: Explicit config file path (overrides auto-discovery)
            cli_args: CLI arguments to use as highest priority overrides
            
        Returns:
            Resolved configuration
        """
        # Start with built-in defaults
        config_data = self._get_default_config_dict()
        
        # Layer 3: User config (if exists)
        user_config = self._load_user_config()
        if user_config:
            config_data = self._merge_config(config_data, user_config)
        
        # Layer 2: Project config (if exists)
        project_config = self._load_project_config(project_root, config_file)
        if project_config:
            config_data = self._merge_config(config_data, project_config)
        
        # Layer 1: CLI arguments (highest priority)
        if cli_args:
            self._cli_overrides = cli_args
            config_data = self._apply_cli_overrides(config_data, cli_args)
        
        # Validate and create final config
        try:
            self._config = MDVisConfig(**config_data)
            return self._config
        except ValidationError as e:
            raise ConfigurationError(f"Invalid configuration: {e}")
    
    def _get_default_config_dict(self) -> Dict[str, Any]:
        """Get default configuration as dictionary."""
        return get_default_config().dict()
    
    def _load_user_config(self) -> Optional[Dict[str, Any]]:
        """Load user-level configuration."""
        # Try XDG config directory first, then fallback to home
        config_dirs = [
            Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')),
            Path.home()
        ]
        
        for config_dir in config_dirs:
            config_path = config_dir / 'mdvis' / 'config.yaml'
            if config_path.exists():
                self._user_config_path = config_path
                return self._load_yaml_file(config_path)
        
        return None
    
    def _load_project_config(
        self, 
        project_root: Optional[Path] = None,
        explicit_config: Optional[Path] = None
    ) -> Optional[Dict[str, Any]]:
        """Load project-level configuration."""
        
        # Use explicit config file if provided
        if explicit_config:
            if explicit_config.exists():
                self._project_config_path = explicit_config
                return self._load_yaml_file(explicit_config)
            else:
                raise ConfigurationError(f"Specified config file not found: {explicit_config}")
        
        # Auto-discover project config
        search_paths = []
        
        if project_root:
            search_paths.extend([
                project_root / 'docs' / 'mdvis.yaml',
                project_root / 'docs' / 'mdvis.yml',
                project_root / '.mdvis.yaml',
                project_root / '.mdvis.yml',
                project_root / 'mdvis.yaml',
                project_root / 'mdvis.yml'
            ])
        
        # Also search current directory
        cwd = Path.cwd()
        search_paths.extend([
            cwd / 'docs' / 'mdvis.yaml',
            cwd / 'docs' / 'mdvis.yml',
            cwd / '.mdvis.yaml',
            cwd / '.mdvis.yml'
        ])
        
        for config_path in search_paths:
            if config_path.exists():
                self._project_config_path = config_path
                return self._load_yaml_file(config_path)
        
        return None
    
    def _load_yaml_file(self, path: Path) -> Dict[str, Any]:
        """Load and parse a YAML configuration file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
                return content if content is not None else {}
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {path}: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error reading config file {path}: {e}")
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge configuration dictionaries.
        
        Override values take precedence, but nested dicts are merged recursively.
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_cli_overrides(self, config: Dict[str, Any], cli_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply CLI argument overrides to configuration.
        
        CLI args use flat keys that map to nested config structure.
        """
        result = config.copy()
        
        # Map CLI args to config paths
        cli_mappings = {
            'verbosity': 'verbosity',
            'include_private': 'output.include_private',
            'no_events': ('events.enabled', lambda x: not x),  # --no-events sets events.enabled=False
            'generate_diagrams': 'visualization.generate_dependency_graph',
            'exclude_patterns': 'project.exclude_patterns',
            'source_position': 'output.source_position',
            'auto_format': 'linting.auto_format',
            'halt_on_errors': 'linting.halt_on_errors'
        }
        
        for cli_key, config_path in cli_mappings.items():
            if cli_key in cli_args:
                value = cli_args[cli_key]
                
                # Handle special transformations
                if isinstance(config_path, tuple):
                    config_path, transform = config_path
                    value = transform(value)
                
                # Set nested value
                self._set_nested_value(result, config_path, value)
        
        return result
    
    def _set_nested_value(self, config: Dict[str, Any], path: str, value: Any) -> None:
        """Set a nested configuration value using dot notation."""
        keys = path.split('.')
        current = config
        
        # Navigate to parent dict
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set final value
        current[keys[-1]] = value
    
    def create_default_config_file(self, output_path: Path, project_name: Optional[str] = None) -> None:
        """Create a default configuration file."""
        config = get_default_config()
        
        # Customize for project if name provided
        if project_name:
            config.project.name = project_name
        
        # Convert to dict and add comments
        config_dict = config.dict()
        
        # Generate YAML with comments
        yaml_content = self._generate_commented_yaml(config_dict)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
    
    def _generate_commented_yaml(self, config: Dict[str, Any]) -> str:
        """Generate YAML with helpful comments."""
        lines = [
            "# MDVis Configuration File",
            "# This file contains project-specific settings for documentation generation.",
            "",
            "# Output verbosity: minimal, standard, or detailed",
            f"verbosity: {config['verbosity']}",
            "",
            "# Project information",
            "project:",
            f"  name: {config['project']['name'] or 'YourProject'}",
            f"  description: {config['project']['description'] or 'Project description'}",
            "  source_paths:",
            "    - src",
            "  exclude_patterns:",
            "    - '**/test_*.py'",
            "    - '**/tests/**'",
            "    - '**/__pycache__/**'",
            "",
            "# Output generation settings",
            "output:",
            f"  structure: {config['output']['structure']}  # mirror or flatten",
            f"  include_private: {str(config['output']['include_private']).lower()}",
            f"  source_position: {config['output']['source_position']}  # top or bottom",
            "",
            "# Event system detection",
            "events:",
            f"  enabled: {str(config['events']['enabled']).lower()}",
            f"  auto_detect: {str(config['events']['auto_detect']).lower()}",
            "  # Add custom patterns here if needed",
            "  patterns: []",
            "",
            "# Code analysis settings", 
            "analysis:",
            f"  detect_async_patterns: {str(config['analysis']['detect_async_patterns']).lower()}",
            f"  detect_type_hints: {str(config['analysis']['detect_type_hints']).lower()}",
            f"  calculate_complexity: {str(config['analysis']['calculate_complexity']).lower()}",
            "",
            "# Visualization generation",
            "visualization:",
            f"  generate_dependency_graph: {str(config['visualization']['generate_dependency_graph']).lower()}",
            f"  generate_event_flow: {str(config['visualization']['generate_event_flow']).lower()}",
            "",
            "# Code linting during processing",
            "linting:",
            f"  enabled: {str(config['linting']['enabled']).lower()}",
            f"  auto_format: {str(config['linting']['auto_format']).lower()}",
            f"  halt_on_errors: {str(config['linting']['halt_on_errors']).lower()}"
        ]
        
        return '\n'.join(lines)
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get information about loaded configuration sources."""
        return {
            'user_config_path': str(self._user_config_path) if self._user_config_path else None,
            'project_config_path': str(self._project_config_path) if self._project_config_path else None,
            'cli_overrides': self._cli_overrides,
            'effective_config': self._config.dict() if self._config else None
        }
    
    @property
    def config(self) -> Optional[MDVisConfig]:
        """Get the currently loaded configuration."""
        return self._config
    
    def validate_paths(self, project_root: Path) -> List[str]:
        """
        Validate that configured paths exist and are accessible.
        
        Returns list of validation errors, empty if all valid.
        """
        errors = []
        
        if not self._config:
            errors.append("No configuration loaded")
            return errors
        
        # Check source paths
        for source_path in self._config.project.source_paths:
            path = project_root / source_path
            if not path.exists():
                errors.append(f"Source path does not exist: {path}")
            elif not path.is_dir():
                errors.append(f"Source path is not a directory: {path}")
        
        # Validate regex patterns in event config
        if self._config.events.enabled:
            for pattern_config in self._config.events.patterns:
                try:
                    import re
                    for pattern in pattern_config.publisher_patterns + pattern_config.subscriber_patterns:
                        re.compile(pattern)
                    re.compile(pattern_config.extract_event_type)
                except re.error as e:
                    errors.append(f"Invalid regex in event pattern '{pattern_config.name}': {e}")
        
        return errors