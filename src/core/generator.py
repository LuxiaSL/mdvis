"""
Generator Module

Enhanced markdown generation that integrates the advanced parser output.
It now produces markdown files that include:
  - A code block with the raw Python source.
  - A structured overview of the file's parsed structure, including:
      - Imports
      - Classes (with methods and nested functions)
      - Top-level functions (with nested functions and call chains)
  - Obsidian-friendly formatting with explicit header anchors and links.
"""

import os
from pathlib import Path
from typing import List

from .parser import parse_file  # our advanced parser
from ..models.code_elements import Module, Class, Function, ImportStatement, Call

# Helper function to generate an anchor from a given text.
def generate_anchor(text: str, prefix: str = "") -> str:
    # Simplistic anchor generator: lowercase, strip spaces, prepend prefix if any.
    anchor = text.lower().replace(" ", "-")
    if prefix:
        return f"{prefix}-{anchor}"
    return anchor

def render_imports(imports: list) -> str:
    """
    Render a list of ImportStatement objects as markdown.
    For modules that look like our codebase, we wrap the module name in Obsidian-style links.
    """
    if not imports:
        return ""
    
    md = "### Imports\n\n"
    for imp in imports:
        if imp.module:
            # Wrap module names in link syntax (assuming the module's markdown file is named after it)
            md += f"- **From** `[[{imp.module}]]` **import**: "
        else:
            md += "- **Import**: "
        # Create a list of names with alias information
        names = [f"`{name}` (as `{alias}`)" if alias else f"`{name}`" for name, alias in imp.names]
        md += ", ".join(names) + "\n"
    return md + "\n"

def render_function(func: Function, level: int = 3) -> str:
    """
    Render a Function object as markdown.
    Includes an Obsidian-friendly anchor so that other pages can link directly to it.
    """
    header = "#" * level
    # Generate an anchor for the function
    anchor = generate_anchor(func.name)
    md = f"{header} Function: `{func.name}` {{#{anchor}}}\n\n"
    if func.docstring:
        md += f"> {func.docstring}\n\n"
    md += f"**Parameters:** {', '.join(func.parameters) if func.parameters else 'None'}\n\n"
    
    if func.calls:
        md += "#### Calls\n\n"
        for call in func.calls:
            chain = ".".join(call.call_chain)
            md += f"- `{chain}`\n"
        md += "\n"
    
    # Render any nested functions recursively
    if func.nested_functions:
        md += "#### Nested Functions\n\n"
        for nested in func.nested_functions:
            md += render_function(nested, level=level+1)
    
    return md

def render_class(cls: Class) -> str:
    """
    Render a Class object as markdown.
    Provides an anchor for direct linking in Obsidian.
    """
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
    """
    Render the entire Module object as structured markdown.
    The module header gets an anchor as well.
    """
    anchor = generate_anchor(module_obj.name, prefix="module")
    md = f"## Module: `{module_obj.name}` {{#{anchor}}}\n\n"
    # Imports section
    md += render_imports(module_obj.imports)
    
    # Classes section
    if module_obj.classes:
        md += "### Classes\n\n"
        for cls in module_obj.classes:
            md += render_class(cls)
    
    # Top-level functions section
    if module_obj.functions:
        md += "### Top-level Functions\n\n"
        for func in module_obj.functions:
            md += render_function(func, level=3) + "\n"
    
    return md

def generate_markdown(file_path: str, output_directory: str) -> Module:
    """
    Generate a markdown file from the provided Python file. The markdown file
    includes:
      - The raw code in a syntax-highlighted code block.
      - A structured overview of the file's parsed structure.
    Returns the parsed Module object (if successful), so it can be added to a global index.
    """
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    file_name = Path(file_path).stem
    markdown_file_name = f"{file_name}.md"
    output_path = output_dir / markdown_file_name

    try:
        with open(file_path, 'r', encoding='utf-8') as src_file:
            code_content = src_file.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

    # Parse the file to get a structured representation.
    try:
        module_obj = parse_file(file_path)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        module_obj = None

    markdown_content = f"# {file_name}\n\n"
    markdown_content += "## Raw Code\n\n"
    markdown_content += "```python\n" + code_content + "\n```\n\n"
    
    if module_obj:
        markdown_content += "## Parsed Structure\n\n"
        markdown_content += render_module_structure(module_obj)
    else:
        markdown_content += "> **Warning:** Parsing failed. No structural details available.\n"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_content)
        print(f"Generated markdown: {output_path}")
    except Exception as e:
        print(f"Error writing {output_path}: {e}")
    
    return module_obj

def generate_dashboard(modules: List[Module], output_directory: str) -> None:
    """
    Generate a dashboard markdown file that aggregates links to all modules.
    Each module is linked via its Obsidian-friendly name.
    """
    dashboard_lines = ["# Codebase Dashboard\n"]
    for module_obj in modules:
        # Each module is assumed to have a markdown file named after it.
        # The link will point to that file. Optionally, we can link to a specific section.
        anchor = generate_anchor(module_obj.name, prefix="module")
        dashboard_lines.append(f"- [[{module_obj.name}#{{#{anchor}}}]]")
    dashboard_content = "\n".join(dashboard_lines)

    output_dir = Path(output_directory)
    dashboard_file = output_dir / "Dashboard.md"
    try:
        with open(dashboard_file, "w", encoding="utf-8") as f:
            f.write(dashboard_content)
        print(f"Generated dashboard: {dashboard_file}")
    except Exception as e:
        print(f"Error writing dashboard {dashboard_file}: {e}")
