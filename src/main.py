"""
Main driver for the codebase markdown visualizer.
Integrates scanning, linting, parsing, markdown generation, and dashboard creation.
"""

import sys
from pathlib import Path

from utils.config import load_config
from core.scanner import scan_for_python_files
from core.linter import lint_file
from core.generator import generate_markdown, generate_dashboard

def main():
    # Load configuration from YAML
    config = load_config()
    root_dir = config.get("root_directory", "./src")
    output_dir = config.get("output_directory", "./output_markdown")
    linters = config.get("linters", {})
    halt_on_errors = config.get("halt_on_errors", True)

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print(f"Scanning for Python files in: {root_dir}")
    python_files = scan_for_python_files(root_dir)
    print(f"Found {len(python_files)} Python files.")

    module_index = []  # Global index for dashboard generation

    for file_path in python_files:
        print(f"\nProcessing file: {file_path}")
        
        # Lint the file
        lint_results = lint_file(file_path, linters)
        stop_processing = False
        for linter, (code, output) in lint_results.items():
            print(f"  [{linter}] Return code: {code}")
            if output.strip():
                print(f"  [{linter}] Output:\n{output}")
            if halt_on_errors and code != 0:
                stop_processing = True

        if stop_processing:
            print("Halting processing due to linting errors.")
            sys.exit(1)

        # Generate markdown file from Python file (with parsed structure)
        module_obj = generate_markdown(file_path, output_dir)
        if module_obj:
            module_index.append(module_obj)
    
    # Generate a dashboard file with links to all modules.
    if module_index:
        generate_dashboard(module_index, output_dir)

if __name__ == "__main__":
    main()
