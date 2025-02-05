"""
Main driver for the codebase markdown visualizer.
Integrates scanning, linting, parsing, markdown generation, and
dashboard creation.
"""

import sys
import argparse
from pathlib import Path

from src.utils.config import load_config
from src.core.scanner import scan_for_python_files
from src.core.linter import lint_file
from src.core.generator import (
    generate_markdown, generate_dashboard, clean_code
)
# Stub for file watcher import.
try:
    from src.core.watcher import start_watching
except ImportError:
    def start_watching(root_dir, output_dir, linters, halt_on_errors):
        print("Watch mode is not yet implemented.")
        sys.exit(0)

def process_file(file_path, root_dir, output_dir, linters, halt_on_errors):
    """
    1) Autoformat code in memory
    2) Lint code
    3) If lint passes, generate markdown
    """
    print(f"\nProcessing file: {file_path}")
    relative_path = Path(file_path).relative_to(Path(root_dir))
    # Read the original file.
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        sys.exit(1)

    # Autoformat the code.
    print("Autoformatting code...")
    formatted_code = clean_code(original_code)

    # Write formatted code to a temporary file.
    import tempfile
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(formatted_code)
        tmp_path = tmp.name

    # Lint the temporary file.
    lint_results = lint_file(tmp_path, linters)
    stop_processing = False
    for linter, (code, output) in lint_results.items():
        print(f"  [{linter}] Return code: {code}")
        if output.strip():
            print(f"  [{linter}] Output:\n{output}")
        if halt_on_errors and code != 0:
            stop_processing = True

    # Clean up the temporary file.
    import os
    os.remove(tmp_path)

    # We'll add the lint warnings to the module object after generation
    module_obj = generate_markdown(
        file_path=file_path,
        root_dir=root_dir,
        output_dir=output_dir,
        source_code=formatted_code,
        relative_path=relative_path
    )

    # If the module object is returned, store any lint messages in .lint_warnings
    if module_obj:
        all_warnings = []
        for linter, (rcode, output) in lint_results.items():
            if output.strip():
                for line in output.strip().splitlines():
                    all_warnings.append(line)
        module_obj.lint_warnings = all_warnings

    return module_obj

def process_all_files(root_dir, output_dir, linters, halt_on_errors):
    """
    Process all Python files under root_dir and generate the dashboard.
    Now attempts to load .gitignore from root_dir to skip ignored files.
    """
    gitignore_path = Path(root_dir) / ".gitignore"
    print(f"Scanning for Python files in: {root_dir}")
    python_files = scan_for_python_files(str(root_dir), str(gitignore_path))
    print(f"Found {len(python_files)} Python files.")

    module_index = []
    for file_path in python_files:
        mod_obj = process_file(file_path, root_dir, output_dir, linters, halt_on_errors)
        if mod_obj:
            module_index.append(mod_obj)

    if module_index:
        generate_dashboard(module_index, output_dir)


def main():
    description = (
        "Generate interlinked markdown documentation from a Python codebase for Obsidian."
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--watch", action="store_true", help="Enable watch mode: monitor for file changes and update documentation incrementally.")
    parser.add_argument("--root", type=str, help="Root directory of the Python codebase (overrides config).")
    parser.add_argument("--output", type=str, help="Output directory for generated markdown files (overrides config).")
    args = parser.parse_args()

    config = load_config()
    root_dir = args.root if args.root else config.get("root_directory", "./src")
    output_dir = args.output if args.output else config.get("output_directory", "./output_markdown")
    linters = config.get("linters", {})
    halt_on_errors = config.get("halt_on_errors", True)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if args.watch:
        print("Watch mode enabled. Monitoring for changes...")
        start_watching(root_dir, output_dir, linters, halt_on_errors)
    else:
        process_all_files(root_dir, output_dir, linters, halt_on_errors)

if __name__ == "__main__":
    main()