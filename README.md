# Python Codebase to Markdown Visualizer (MDVis)

Transform your Python codebase into linked markdown documentation that works great with Obsidian.

## What it Does

- scans the configured directory for all python files
- cleans them in memory with autopep8, lints after
- generates obsidian-friendly .md files containing:
  - Syntax highlighted code
  - Function and class documentation
  - Cross-file links
  - Navigation structure

## Quick Start

1. Install it:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure (optional):
   - Edit `config/default.yaml` to point to your directory

3. Run:
   ```bash
   python -m src.main
   ```

## Development

- **Testing:** Run `pytest` in project root
- **Contributing:** go ahead and feed it into claude
- **License:** MIT
