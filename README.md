# Python Codebase to Markdown Visualizer

This project transforms a Python codebase into interlinked markdown files optimized for Obsidian.

## Features

- **Scanning:** Recursively scans a specified directory for Python files.
- **Linting:** Integrates with external linting tools (e.g., flake8) to check code quality.
- **Markdown Generation:** Converts each Python file into a markdown file with syntax highlighting.
- **Modularity:** Designed with a modular architecture for future extension (e.g., AST parsing and visualization).

## Setup

1. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration:**

   The default configuration is located in `config/default.yaml`. You can modify it as needed.

3. **Run the Application:**

   ```bash
   python src/main.py
   ```

## Testing

Tests are located in the `tests/` directory. Run them using your favorite test runner (e.g., `pytest`).

## Project Structure

```
README.md
config/
  default.yaml
pyproject.toml
requirements.txt
setup.py
src/
  core/
    __init__.py
    generator.py
    linter.py
    parser.py
    scanner.py
  main.py
  models/
    __init__.py
    code_elements.py
  utils/
    __init__.py
    config.py
tests/
  __init__.py
  test_generator.py
  test_linter.py
  test_parser.py
  test_scanner.py
```