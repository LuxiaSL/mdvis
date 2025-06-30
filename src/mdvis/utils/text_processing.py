"""
Text processing utilities for mdvis.

Common text manipulation functions used throughout the codebase.
"""

import re
from typing import List, Optional, Tuple
from pathlib import Path


def sanitize_anchor(text: str) -> str:
    """
    Sanitize text for use as an Obsidian anchor.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized anchor string
    """
    # Convert to lowercase and replace spaces/underscores with hyphens
    sanitized = re.sub(r'[_\s]+', '-', text.lower())
    # Remove any characters that aren't alphanumeric or hyphens
    sanitized = re.sub(r'[^a-z0-9\-]', '', sanitized)
    # Remove leading/trailing hyphens and collapse multiple hyphens
    sanitized = re.sub(r'-+', '-', sanitized).strip('-')
    return sanitized


def generate_wikilink(
    target: str, 
    anchor: Optional[str] = None, 
    display_text: Optional[str] = None
) -> str:
    """
    Generate an Obsidian wikilink.
    
    Args:
        target: Target file/page name
        anchor: Optional anchor within the target
        display_text: Optional display text (defaults to target)
        
    Returns:
        Formatted wikilink
    """
    link = f"[[{target}"
    
    if anchor:
        link += f"#{anchor}"
    
    if display_text and display_text != target:
        link += f"|{display_text}"
    
    link += "]]"
    return link


def escape_markdown(text: str) -> str:
    """
    Escape special markdown characters in text.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text safe for markdown
    """
    # Escape common markdown special characters
    escapes = {
        '\\': '\\\\',
        '`': '\\`',
        '*': '\\*',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '[': '\\[',
        ']': '\\]',
        '(': '\\(',
        ')': '\\)',
        '#': '\\#',
        '+': '\\+',
        '-': '\\-',
        '.': '\\.',
        '!': '\\!',
        '|': '\\|'
    }
    
    for char, escape in escapes.items():
        text = text.replace(char, escape)
    
    return text


def format_code_block(code: str, language: str = "python") -> str:
    """
    Format code in a markdown code block.
    
    Args:
        code: Source code to format
        language: Language for syntax highlighting
        
    Returns:
        Formatted code block
    """
    return f"```{language}\n{code}\n```"


def format_inline_code(text: str) -> str:
    """
    Format text as inline code.
    
    Args:
        text: Text to format
        
    Returns:
        Formatted inline code
    """
    return f"`{text}`"


def truncate_with_ellipsis(text: str, max_length: int = 100) -> str:
    """
    Truncate text with ellipsis if it exceeds max length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def extract_summary_sentence(docstring: str) -> str:
    """
    Extract the first sentence from a docstring as a summary.
    
    Args:
        docstring: Full docstring text
        
    Returns:
        First sentence as summary
    """
    if not docstring:
        return ""
    
    # Split on common sentence endings
    sentences = re.split(r'[.!?]+\s+', docstring.strip())
    if sentences:
        return sentences[0].strip() + "."
    
    return docstring.strip()


def humanize_identifier(identifier: str) -> str:
    """
    Convert a programming identifier to human-readable text.
    
    Args:
        identifier: Programming identifier (snake_case, camelCase, etc.)
        
    Returns:
        Human-readable text
    """
    # Handle snake_case
    text = identifier.replace('_', ' ')
    
    # Handle camelCase and PascalCase
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # Handle acronyms (e.g., XMLParser -> XML Parser)
    text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', text)
    
    return text.strip()


def normalize_line_endings(text: str) -> str:
    """
    Normalize line endings to Unix-style (LF).
    
    Args:
        text: Text with potentially mixed line endings
        
    Returns:
        Text with normalized line endings
    """
    # Convert Windows CRLF and old Mac CR to Unix LF
    return text.replace('\r\n', '\n').replace('\r', '\n')


def count_non_empty_lines(text: str) -> int:
    """
    Count non-empty lines in text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Number of non-empty lines
    """
    return len([line for line in text.splitlines() if line.strip()])


def relative_path_to_link(source_path: Path, target_path: Path) -> str:
    """
    Convert a relative file path to an Obsidian-compatible link path.
    
    Args:
        source_path: Path of the source file
        target_path: Path of the target file
        
    Returns:
        Relative link path suitable for Obsidian
    """
    try:
        # Get relative path from source to target
        relative = target_path.relative_to(source_path.parent)
        # Convert to string and remove .md extension for Obsidian
        link_path = str(relative)
        if link_path.endswith('.md'):
            link_path = link_path[:-3]
        return link_path
    except ValueError:
        # If relative path fails, use target stem
        return target_path.stem


def format_parameter_list(params: List[Tuple[str, Optional[str], Optional[str]]]) -> str:
    """
    Format a list of parameters for display.
    
    Args:
        params: List of (name, type, default) tuples
        
    Returns:
        Formatted parameter string
    """
    if not params:
        return "None"
    
    formatted = []
    for name, param_type, default in params:
        param_str = name
        if param_type:
            param_str += f": {param_type}"
        if default:
            param_str += f" = {default}"
        formatted.append(param_str)
    
    return ", ".join(formatted)


def extract_first_paragraph(text: str) -> str:
    """
    Extract the first paragraph from text.
    
    Args:
        text: Multi-paragraph text
        
    Returns:
        First paragraph only
    """
    if not text:
        return ""
    
    paragraphs = text.strip().split('\n\n')
    return paragraphs[0].strip() if paragraphs else ""


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"