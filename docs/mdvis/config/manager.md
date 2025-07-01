# manager

> Configuration manager with multi-layer resolution.

Handles the priority chain: CLI Args → Project Config → User Config → Built-in Defaults

## Overview

- **Classes:** 2
- **Functions:** 0
- **Lines of Code:** 338

## Imports
- **import** `os`
- **import** `yaml`
- **from** `pathlib` **import** `Path`
- **from** `typing` **import** `Any, Dict, List, Optional, Union`
- **from** `pydantic` **import** `ValidationError`
- **from** `schema` **import** `MDVisConfig, get_default_config`

## Classes
### ConfigurationError {#class-configurationerror}

> Configuration-related error.

**Inherits from:** `Exception`

### ConfigManager {#class-configmanager}

> Manages configuration loading and resolution with multiple layers.

Priority order (highest to lowest):
1. CLI arguments (runtime behavior)
2. Project config file (./docs/mdvis.yaml or specified path)
3. User config file (~/.config/mdvis/config.yaml)  
4. Built-in defaults


#### Methods
##### __init__ {#method-init}


**Signature:** `def __init__(self)`
##### load_config {#method-load-config}

> Load configuration with multi-layer resolution.

**Signature:** `def load_config(self, project_root: Optional[Path] = None, config_file: Optional[Path] = None, cli_args: Optional[Dict[str, Any]] = None) -> MDVisConfig`
##### _get_default_config_dict {#method-get-default-config-dict}

> Get default configuration as dictionary..

**Signature:** `def _get_default_config_dict(self) -> Dict[str, Any]`
##### _load_user_config {#method-load-user-config}

> Load user-level configuration..

**Signature:** `def _load_user_config(self) -> Optional[Dict[str, Any]]`
##### _load_project_config {#method-load-project-config}

> Load project-level configuration..

**Signature:** `def _load_project_config(self, project_root: Optional[Path] = None, explicit_config: Optional[Path] = None) -> Optional[Dict[str, Any]]`
##### _load_yaml_file {#method-load-yaml-file}

> Load and parse a YAML configuration file..

**Signature:** `def _load_yaml_file(self, path: Path) -> Dict[str, Any]`
##### _merge_config {#method-merge-config}

> Deep merge configuration dictionaries.

**Signature:** `def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]`
##### _apply_cli_overrides {#method-apply-cli-overrides}

> Apply CLI argument overrides to configuration.

**Signature:** `def _apply_cli_overrides(self, config: Dict[str, Any], cli_args: Dict[str, Any]) -> Dict[str, Any]`
##### _set_nested_value {#method-set-nested-value}

> Set a nested configuration value using dot notation..

**Signature:** `def _set_nested_value(self, config: Dict[str, Any], path: str, value: Any) -> None`
##### create_default_config_file {#method-create-default-config-file}

> Create a default configuration file..

**Signature:** `def create_default_config_file(self, output_path: Path, project_name: Optional[str] = None) -> None`
##### _generate_commented_yaml {#method-generate-commented-yaml}

> Generate YAML with helpful comments..

**Signature:** `def _generate_commented_yaml(self, config: Dict[str, Any]) -> str`
##### get_config_info {#method-get-config-info}

> Get information about loaded configuration sources..

**Signature:** `def get_config_info(self) -> Dict[str, Any]`
##### config {#method-config}

> Get the currently loaded configuration..

**Signature:** `def config(self) -> Optional[MDVisConfig]`
##### validate_paths {#method-validate-paths}

> Validate that configured paths exist and are accessible.

**Signature:** `def validate_paths(self, project_root: Path) -> List[str]`

