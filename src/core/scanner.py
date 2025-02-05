"""
Scanner Module

Recursively scans a specified directory for Python (.py) files.
"""

import os
from pathlib import Path
from typing import Generator, List

def scan_for_python_files(directory: str) -> List[str]:
    """
    Recursively scan the given directory for .py files.
    Raises FileNotFoundError if the directory does not exist.
    
    :param directory: The root directory to scan.
    :return: A list of absolute file paths.
    """
    path_obj = Path(directory)
    if not path_obj.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    python_files = []
    # Use rglob to recursively search for *.py files
    for file_path in path_obj.rglob("*.py"):
        python_files.append(str(file_path.resolve()))
    return python_files

def scan_for_python_files_generator(directory: str) -> Generator[str, None, None]:
    """
    Generator version for scanning Python files.
    
    :param directory: The root directory to scan.
    :yield: Absolute file path of each Python file found.
    """
    path_obj = Path(directory)
    if not path_obj.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    for file_path in path_obj.rglob("*.py"):
        yield str(file_path.resolve())
