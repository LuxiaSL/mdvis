"""
Generator Module

Enhanced markdown generation that integrates the advanced parser output.
It produces markdown files that include:
  - YAML frontmatter with metadata.
  - A syntax-highlighted code block with the raw (and autoformatted) code.
  - A structured overview of the file's parsed structure.
  - Obsidian-friendly links and anchors.

Before generating the markdown, the source code is autoformatted using Black
to correct style issues (e.g. line length, whitespace). The autoformatting is
done in memory so that the source files remain unmodified.
"""

from pathlib import Path
from typing import List, Optional

from src.core.parser import parse_file  # our advanced parser
from src.models.code_elements import (
    Module,
    Class,
    Function
)
from src.utils.config import load_config  # for configuration flags
from src.core.visualizer import generate_global_dependency_diagram
import autopep8


def generate_anchor(text: str, prefix: str = "") -> str:
    """Generate a simplified anchor by converting text to lowercase and
    replacing spaces with dashes. A prefix is prepended if provided."""
    anchor = text.lower().replace(" ", "-")
    return f"{prefix}-{anchor}" if prefix else anchor


def generate_frontmatter(module_obj: Module) -> str:
    """Generate YAML frontmatter for a module based on its metadata."""
    frontmatter_lines = [
        "---",
        f"title: {module_obj.name}",
        f"file_path: {module_obj.file_path}",
        f"classes: {len(module_obj.classes)}",
        f"functions: {len(module_obj.functions)}",
        f"imports: {len(module_obj.imports)}",
        "tags: [codebase]",
        "---",
        ""
    ]
    return "\n".join(frontmatter_lines)


def render_imports(imports: list) -> str:
    """Render a list of import statements as markdown."""
    if not imports:
        return ""
    md = "### Imports\n\n"
    for imp in imports:
        if imp.module:
            md += f"- **From** `[[{imp.module}]]` **import**: "
        else:
            md += "- **Import**: "
        names = [
            f"`{name}` (as `{alias}`)" if alias else f"`{name}`"
            for name, alias in imp.names]
        md += ", ".join(names) + "\n"
    return md + "\n"


def render_function(func: Function, level: int = 3) -> str:
    """Render as markdown with an Obsidian-friendly anchor."""
    header = "#" * level
    anchor = generate_anchor(func.name)
    md = f"{header} Function: `{func.name}` {{#{anchor}}}\n\n"
    if func.docstring:
        md += f"> {func.docstring}\n\n"
    md += (
        f"**Parameters:** "
        f"{', '.join(func.parameters) if func.parameters else 'None'}\n\n"
    )
    if func.calls:
        md += "#### Calls\n\n"
        for call in func.calls:
            chain = ".".join(call.call_chain)
            md += f"- `{chain}`\n"
        md += "\n"
    if func.nested_functions:
        md += "#### Nested Functions\n\n"
        for nested in func.nested_functions:
            md += render_function(nested, level=level + 1)
    return md


def render_class(cls: Class) -> str:
    """Render a class as markdown with an anchor and its methods."""
    anchor = generate_anchor(cls.name, prefix="class")
    md = f"## Class: `{cls.name}` {{#{anchor}}}\n\n"
    if cls.docstring:
        md += f"> {cls.docstring}\n\n"
    if cls.methods:
        md += "### Methods\n\n"
        for method in cls.methods:
            md += render_function(method, level=4) + "\n"
    return md + "\n"


def render_module_structure(module_obj: Module) -> str:
    """Render the entire module structure as markdown."""
    anchor = generate_anchor(module_obj.name, prefix="module")
    md = f"## Module: `{module_obj.name}` {{#{anchor}}}\n\n"
    md += render_imports(module_obj.imports)
    if module_obj.classes:
        md += "### Classes\n\n"
        for cls in module_obj.classes:
            md += render_class(cls)
    if module_obj.functions:
        md += "### Top-level Functions\n\n"
        for func in module_obj.functions:
            md += render_function(func, level=3) + "\n"
    return md


def clean_code(source_code: str) -> str:
    """
    Autoformat the given source code using autopep8
    """ 
    try:
        formatted_code = autopep8.fix_code(source_code)
        return formatted_code
    except Exception as e:
        print(f"Warning: Code formatting failed: {e}")
        return source_code


def generate_markdown(
    file_path: str,
    root_dir: str,
    output_dir: str,
    source_code: Optional[str] = None,
    relative_path: Optional[Path] = None
) -> Module:
    """
    Generate a markdown file from a Python file. The folder structure
    under 'output_dir' will mirror the file's relative path under 'root_dir'.
    For example, if file_path is 'src/app/utils/foo.py' and root_dir='src',
    the markdown file will be created at 'output_dir/app/utils/foo.md'.
    """

    if relative_path is None:
        # If for some reason it's not provided, fall back to a simple approach
        # (i.e., no nested structure)
        relative_path = Path(file_path).name

    # The folder structure we want to replicate:
    output_subdir = Path(output_dir) / relative_path.parent
    output_subdir.mkdir(parents=True, exist_ok=True)

    # The final name for the Markdown file (same base name, .md extension)
    markdown_file_name = f"{Path(file_path).stem}.md"
    output_path = output_subdir / markdown_file_name

    # If no source_code is provided, read from the file
    if source_code is None:
        try:
            with open(file_path, "r", encoding="utf-8") as src_file:
                code_content = src_file.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    else:
        code_content = source_code

    # Parse the file to obtain structure, etc.
    try:
        module_obj = parse_file(file_path)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        module_obj = None

    # Build markdown content
    markdown_content = ""
    if module_obj:
        markdown_content += generate_frontmatter(module_obj)
    file_name = Path(file_path).stem
    markdown_content += f"# {file_name}\n\n"
    markdown_content += "## Raw Code\n\n"
    markdown_content += "```python\n" + code_content + "\n```\n\n"
    
    if module_obj:
        markdown_content += "## Parsed Structure\n\n"
        markdown_content += render_module_structure(module_obj)
    else:
        markdown_content += (
            "> **Warning:** Parsing failed. "
            "No structural details available.\n"
        )

    # Write to the correct subfolder
    try:
        with open(output_path, "w", encoding="utf-8") as md_file:
            md_file.write(markdown_content)
        print(f"Generated markdown: {output_path}")
    except Exception as e:
        print(f"Error writing {output_path}: {e}")

    return module_obj



def generate_dashboard(modules: List[Module], output_directory: str) -> None:
    """
    Generate a dashboard markdown file that aggregates links to all modules.
    If diagram generation is enabled in the configuration and modules exist,
    append a Mermaid diagram showing module dependencies.
    """
    config = load_config()
    generate_diagrams = config.get("generate_diagrams", False)
    dashboard_lines = ["# Codebase Dashboard"]

    if modules:
        for module_obj in modules:
            anchor = generate_anchor(module_obj.name, prefix="module")
            dashboard_lines.append(f"- [[{module_obj.name}#{{#{anchor}}}]]")

    if modules and generate_diagrams:
        diagram = generate_global_dependency_diagram(modules)
        if diagram:
            dashboard_lines.append("")
            dashboard_lines.append("## Module Dependency Diagram")
            dashboard_lines.append("")
            dashboard_lines.append(diagram)

    dashboard_content = "\n".join(dashboard_lines)
    output_dir = Path(output_directory)
    dashboard_file = output_dir / "Dashboard.md"
    try:
        with open(dashboard_file, "w", encoding="utf-8") as f:
            f.write(dashboard_content)
        print(f"Generated dashboard: {dashboard_file}")
    except Exception as e:
        print(f"Error writing dashboard {dashboard_file}: {e}")
