"""
Scanner Module

Recursively scans a specified directory for Python (.py) files,
optionally respecting a .gitignore pattern list.
"""

from pathlib import Path
from typing import List, Optional

import pathspec

def load_gitignore_patterns(gitignore_path: str) -> pathspec.PathSpec:
    """
    Load .gitignore-style patterns from the specified file into a PathSpec object.
    If the file doesn't exist, return an empty PathSpec.
    """
    gitignore_file = Path(gitignore_path)
    if not gitignore_file.exists():
        return pathspec.PathSpec.from_lines('gitignore', [])
    
    with open(gitignore_file, 'r', encoding='utf-8') as f:
        patterns = f.readlines()
    return pathspec.PathSpec.from_lines('gitignore', patterns)

def scan_for_python_files(
    directory: str, 
    gitignore_path: Optional[str] = None
) -> List[str]:
    """
    Recursively scan the given directory for .py files.
    If gitignore_path is provided, skip files matching the .gitignore patterns.
    """
    path_obj = Path(directory)
    if not path_obj.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    # Load the .gitignore patterns if a path is provided.
    ignore_spec = pathspec.PathSpec.from_lines('gitignore', [])
    if gitignore_path:
        ignore_spec = load_gitignore_patterns(gitignore_path)

    python_files = []
    for file_path in path_obj.rglob("*.py"):
        relative_path = file_path.relative_to(path_obj)
        # Check if this file matches any gitignore patterns.
        if ignore_spec.match_file(str(relative_path)):
            # Skip if it matches the .gitignore patterns.
            continue
        python_files.append(str(file_path.resolve()))

    return python_files
