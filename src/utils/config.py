"""
Configuration Utilities

Provides functionality to load configuration from a YAML file.
"""

import os
import yaml
from pathlib import Path

DEFAULT_CONFIG_PATH = os.path.join("config", "default.yaml")

def load_config(config_path: str = DEFAULT_CONFIG_PATH) -> dict:
    """
    Load the configuration from the specified YAML file.
    
    :param config_path: Path to the YAML configuration file.
    :return: Configuration as a dictionary.
    """
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"Configuration file {config_path} not found. Using empty configuration.")
        return {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config if config is not None else {}
    except Exception as e:
        print(f"Error loading configuration file {config_path}: {e}")
        return {}
