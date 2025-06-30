"""
MDVis - Transform Python codebases into interlinked Obsidian-compatible markdown documentation.

A powerful documentation generator that analyzes Python code and creates rich,
navigable documentation with smart cross-references, type information, and
dependency visualizations.
"""

__version__ = "0.3.0"
__author__ = "Luxia"
__email__ = "mail.luxia@gmail.com"

from .config.schema import MDVisConfig
from .config.manager import ConfigManager
from .core.processor import DocumentationProcessor
from .models.elements import Module, Class, Function

__all__ = [
    "MDVisConfig",
    "ConfigManager", 
    "DocumentationProcessor",
    "Module",
    "Class", 
    "Function",
]