"""
Linter Module

Provides functionality to run configured linting tools on a Python file.
"""

import subprocess
from typing import Tuple, Dict

def run_linter(linter_command: str, file_path: str) -> Tuple[int, str]:
    """
    Run the given linter command on the specified file.
    
    :param linter_command: The command for the linter (e.g., 'flake8').
    :param file_path: The file to lint.
    :return: A tuple (return_code, output)
    """
    command = [linter_command, file_path]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )
        return (result.returncode, result.stdout + result.stderr)
    except Exception as e:
        return (-1, f"Linter error: {str(e)}")

def lint_file(
        file_path: str,
        linters: Dict[str, str]
    ) -> Dict[str, Tuple[int, str]]:
    """
    Run all configured linters on a file.
    
    :param file_path: The Python file to lint.
    :param linters: A dictionary with linter names
    as keys and command names as values.
    :return: Dictionary with linter results.
    """
    results = {}
    for linter_name, linter_command in linters.items():
        results[linter_name] = run_linter(linter_command, file_path)
    return results
