"""
Generator Module

This module takes a parsed Python Module (from your parser)
and generates a fully structured Obsidian Markdown document.
It leverages Obsidian’s features like YAML frontmatter,
block references, callouts, collapsible sections, and Mermaid diagrams.
"""

import autopep8
from pathlib import Path
from typing import List, Optional
from src.core.parser import parse_file
from src.models.code_elements import Module, Class, Function, ImportStatement
from src.utils.config import load_config
from src.core.visualizer import generate_global_dependency_diagram

# --- Helper Functions ---

def generate_anchor(label: str, prefix: str = "") -> str:
    """
    Generate an anchor by lowercasing the label and replacing spaces with dashes.
    Used in markdown as {#prefix-label}.
    """
    anchor = label.lower().replace(" ", "-")
    return f"{prefix}-{anchor}" if prefix else anchor

def generate_frontmatter(module_obj: Module) -> str:
    """
    Generate YAML frontmatter with rich metadata and robust tags.
    We include counts of classes, functions, imports, events, and code metrics.
    """
    # Basic tags
    tags = ["autogenerated", "python", "module"]
    if module_obj.classes:
        tags.append("OOP")
    if module_obj.functions:
        tags.append("functional")
    
    # Collect additional stats
    stats = {
        "classes": len(module_obj.classes),
        "functions": len(module_obj.functions),
        "imports": len(module_obj.imports),
        "lines_of_code": module_obj.source.count("\n") if module_obj.source else 0,
        "lint_errors": len(module_obj.lint_warnings),
        "events_published": len(module_obj.events_published) if hasattr(module_obj, "events_published") else 0,
        "events_subscribed": len(module_obj.events_subscribed) if hasattr(module_obj, "events_subscribed") else 0,
    }

    # Convert stats to YAML lines
    stats_lines = "\n".join([f"  {k}: {v}" for k, v in stats.items()])
    tag_lines = "\n".join([f"  - {t}" for t in tags])

    frontmatter_lines = [
        "---",
        f"title: {module_obj.name}",
        "doc_type: module",
        f"file_path: {module_obj.file_path}",
        "stats:",
        stats_lines,
        "tags:",
        tag_lines,
        "---",
        ""
    ]
    return "\n".join(frontmatter_lines)

def render_imports(imports: List[ImportStatement]) -> str:
    """
    Render imports as a Markdown section.  
    If 'module' is None, it's a plain "import X", otherwise "from X import ...".
    """
    if not imports:
        return ""
    md = "### Imports\n\n"
    for imp in imports:
        if imp.module:
            md += f"- **From** [[{imp.module}]] **import**:\n"
        else:
            md += "- **Import**:\n"
        for (name, alias) in imp.names:
            alias_part = f" as `{alias}`" if alias else ""
            md += f"  - `{name}`{alias_part}\n"
    return md + "\n"

def render_docstring_as_callout(docstring: str) -> str:
    """
    Wrap a docstring in an Obsidian [!info] callout block.
    """
    lines = ["> [!info] Docstring"]
    for line in docstring.splitlines():
        # Escape any leading > to avoid nested blockquotes
        if line.strip().startswith(">"):
            line = "\\" + line
        lines.append(f"> {line}")
    return "\n".join(lines) + "\n"

def render_event_usage(entity_name: str, published: List, subscribed: List) -> str:
    """
    Render event usage for a function, class, or module.
    Creates collapsible sections for events published and subscribed.
    """
    if not published and not subscribed:
        return ""
    
    md = "\n<details>\n<summary>Event Usage for " + entity_name + "</summary>\n\n"
    if published:
        md += "#### Events Published\n"
        for event in published:
            md += f"- `{event.event_type}`"
            if event.priority is not None:
                md += f" (priority: {event.priority})"
            md += "\n"
    if subscribed:
        md += "\n#### Events Subscribed\n"
        for event in subscribed:
            md += f"- `{event.event_type}`\n"
    md += "\n</details>\n"
    return md

# --- Renderers for Functions, Classes, and Modules ---

def render_function(func: Function, level: int = 3) -> str:
    """
    Render a function or method.
    Uses anchors and block references.
    Also adds a collapsible section for any event usage.
    """
    header = "#" * level
    is_method = bool(func.parent_class)
    anchor_prefix = "method" if is_method else "function"
    anchor = generate_anchor(func.name, prefix=anchor_prefix)
    title_text = "Method" if is_method else "Function"
    md = f"{header} {title_text}: `{func.name}` {{#{anchor}}}\n"
    md += f"^{anchor}\n\n"
    
    # Render docstring as a callout
    if func.docstring:
        md += render_docstring_as_callout(func.docstring) + "\n"
    
    # Basic information
    md += f"**Parameters:** {', '.join(func.parameters) if func.parameters else 'None'}\n\n"
    
    # Decorators, if any
    if func.decorators:
        md += "**Decorators:**\n\n"
        for dec in func.decorators:
            md += f"- `{dec}`\n"
        md += "\n"
    
    # Calls within the function
    if func.calls:
        md += "#### Calls\n\n"
        for call_obj in func.calls:
            chain = ".".join(call_obj.call_chain)
            md += f"- `{chain}`\n"
        md += "\n"
    
    # Render event usage (if available)
    md += render_event_usage(func.name, func.events_published, func.events_subscribed)
    
    # Nested functions (recursively rendered)
    if func.nested_functions:
        md += "#### Nested Functions\n\n"
        for nested in func.nested_functions:
            md += render_function(nested, level=level + 1)
    
    return md

def render_class(cls: Class) -> str:
    """
    Render a class with its documentation.
    Includes an anchor, block reference, docstring, inheritance, and methods.
    Also shows event usage if present.
    """
    anchor = generate_anchor(cls.name, prefix="class")
    md = f"## Class: `{cls.name}` {{#{anchor}}}\n"
    md += f"^class-{anchor}\n\n"
    
    # Docstring
    if cls.docstring:
        md += render_docstring_as_callout(cls.docstring) + "\n"
    
    # Base classes (inheritance)
    if cls.base_classes:
        base_list = ", ".join(cls.base_classes)
        md += f"**Extends:** {base_list}\n\n"
    
    # Render events at the class level, if any
    md += render_event_usage(cls.name, cls.events_published, cls.events_subscribed)
    
    # Methods
    if cls.methods:
        md += "### Methods\n\n"
        for method in cls.methods:
            md += render_function(method, level=4) + "\n"
    
    # (Optionally, you could render inner classes here)
    
    return md + "\n"

def render_module_structure(module_obj: Module) -> str:
    """
    Render the entire module's structure, including:
      - Imports
      - Classes and their methods
      - Top-level functions
      - (Optional) A summary of event usage at the module level.
    """
    anchor = generate_anchor(module_obj.name, prefix="module")
    md = f"## Module: `{module_obj.name}` {{#{anchor}}}\n"
    md += f"^{anchor}\n\n"
    
    # Imports
    md += render_imports(module_obj.imports)
    
    # Module-level event usage (if any, aggregated from the module)
    md += render_event_usage(module_obj.name, module_obj.events_published, module_obj.events_subscribed)
    
    # Classes
    if module_obj.classes:
        md += "### Classes\n\n"
        for cls in module_obj.classes:
            md += render_class(cls)
    
    # Top-level functions
    if module_obj.functions:
        md += "### Top-Level Functions\n\n"
        for func in module_obj.functions:
            md += render_function(func, level=3) + "\n"
    
    return md

def render_lint_warnings(module_obj: Module) -> str:
    """
    Render lint warnings in an Obsidian [!warning] callout.
    """
    if not module_obj.lint_warnings:
        return ""
    md = "## Lint Warnings\n\n"
    md += "> [!warning] Lint Issues\n"
    for warning in module_obj.lint_warnings:
        md += f"> - {warning}\n"
    return md + "\n"

def render_todos(module_obj: Module) -> str:
    """
    Convert captured TODO items into a Markdown task list.
    """
    if not module_obj.todos:
        return ""
    md = "## TODOs\n\n"
    for todo in module_obj.todos:
        md += f"- [ ] {todo}\n"
    return md + "\n"

def clean_code(source_code: str) -> str:
    """
    Autoformat code using autopep8 (in-memory).
    """
    try:
        return autopep8.fix_code(source_code)
    except Exception as e:
        print(f"Warning: Code formatting failed: {e}")
        return source_code

def generate_markdown(
    file_path: str,
    root_dir: str,
    output_dir: str,
    source_code: Optional[str] = None,
    relative_path: Optional[Path] = None
) -> Optional[Module]:
    """
    Create a Markdown document for a Python file.
    Preserves the folder structure under 'output_dir' and generates a richly formatted
    Obsidian document with frontmatter, raw code, lint warnings, TODOs, and parsed structure.
    """
    if relative_path is None:
        relative_path = Path(file_path).relative_to(root_dir)
    
    output_subdir = Path(output_dir) / relative_path.parent
    output_subdir.mkdir(parents=True, exist_ok=True)
    markdown_file_name = f"{Path(file_path).stem}.md"
    output_path = output_subdir / markdown_file_name

    # Read source code if not provided
    if source_code is None:
        try:
            with open(file_path, "r", encoding="utf-8") as src_file:
                code_content = src_file.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    else:
        code_content = source_code

    # Parse the file structure
    try:
        module_obj = parse_file(file_path)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        module_obj = None

    # Build the final Markdown content
    markdown_content = ""
    if module_obj:
        markdown_content += generate_frontmatter(module_obj)
    markdown_content += f"# {Path(file_path).stem}\n\n"
    
    # Provide a formatted raw code block
    markdown_content += "## Raw Code\n\n"
    markdown_content += "```python\n" + clean_code(code_content) + "\n```\n\n"
    
    if module_obj:
        markdown_content += render_lint_warnings(module_obj)
        markdown_content += render_todos(module_obj)
        markdown_content += "## Parsed Structure\n\n"
        markdown_content += render_module_structure(module_obj)
    else:
        markdown_content += "> **Warning:** Parsing failed. No structural details available.\n"
    
    # Write the output to disk
    try:
        with open(output_path, "w", encoding="utf-8") as md_file:
            md_file.write(markdown_content)
        print(f"Generated markdown: {output_path}")
    except Exception as e:
        print(f"Error writing {output_path}: {e}")

    return module_obj

def generate_dashboard(modules: List[Module], output_directory: str) -> None:
    """
    Produce a central 'Dashboard.md' file that lists all modules (with links to anchors)
    and optionally includes a Mermaid diagram of module dependencies.
    """
    config = load_config()
    generate_diagrams = config.get("generate_diagrams", False)
    
    lines = ["# Codebase Dashboard", ""]
    lines.append("## Module Index\n")
    for m in modules:
        anchor = generate_anchor(m.name, prefix="module")
        # Link using the Obsidian anchor format: [[ModuleName#module-modulename|ModuleName]]
        link = f"[[{m.name}#{anchor}|{m.name}]]"
        lines.append(f"- {link} (Classes: {len(m.classes)}, Functions: {len(m.functions)})")
    
    # Optionally include a Mermaid diagram for module dependencies
    if modules and generate_diagrams:
        lines.append("")
        lines.append("## Module Dependency Diagram\n")
        mermaid_code = generate_global_dependency_diagram(modules)
        if mermaid_code:
            lines.append(mermaid_code)
    
    dashboard_content = "\n".join(lines)
    output_dir = Path(output_directory)
    dashboard_file = output_dir / "Dashboard.md"
    try:
        with open(dashboard_file, "w", encoding="utf-8") as f:
            f.write(dashboard_content)
        print(f"Generated dashboard: {dashboard_file}")
    except Exception as e:
        print(f"Error writing dashboard {dashboard_file}: {e}")
