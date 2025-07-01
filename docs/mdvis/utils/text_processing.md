# text_processing

> Text processing utilities for mdvis.

Common text manipulation functions used throughout the codebase.

## Overview

- **Classes:** 0
- **Functions:** 14
- **Lines of Code:** 289

## Imports
- **import** `re`
- **from** `typing` **import** `List, Optional, Tuple`
- **from** `pathlib` **import** `Path`


## Functions
### sanitize_anchor {#function-sanitize-anchor}

> Sanitize text for use as an Obsidian anchor.

Args:
    text: Input text to sanitize
    
Returns:
    Sanitized anchor string

**Signature:** `def sanitize_anchor(text: str) -> str`
### generate_wikilink {#function-generate-wikilink}

> Generate an Obsidian wikilink.

Args:
    target: Target file/page name
    anchor: Optional anchor within the target
    display_text: Optional display text (defaults to target)
    
Returns:
    Formatted wikilink

**Signature:** `def generate_wikilink(target: str, anchor: Optional[str] = None, display_text: Optional[str] = None) -> str`
### escape_markdown {#function-escape-markdown}

> Escape special markdown characters in text.

Args:
    text: Text to escape
    
Returns:
    Escaped text safe for markdown

**Signature:** `def escape_markdown(text: str) -> str`
### format_code_block {#function-format-code-block}

> Format code in a markdown code block.

Args:
    code: Source code to format
    language: Language for syntax highlighting
    
Returns:
    Formatted code block

**Signature:** `def format_code_block(code: str, language: str = 'python') -> str`
### format_inline_code {#function-format-inline-code}

> Format text as inline code.

Args:
    text: Text to format
    
Returns:
    Formatted inline code

**Signature:** `def format_inline_code(text: str) -> str`
### truncate_with_ellipsis {#function-truncate-with-ellipsis}

> Truncate text with ellipsis if it exceeds max length.

Args:
    text: Text to truncate
    max_length: Maximum length before truncation
    
Returns:
    Truncated text with ellipsis if needed

**Signature:** `def truncate_with_ellipsis(text: str, max_length: int = 100) -> str`
### extract_summary_sentence {#function-extract-summary-sentence}

> Extract the first sentence from a docstring as a summary.

Args:
    docstring: Full docstring text
    
Returns:
    First sentence as summary

**Signature:** `def extract_summary_sentence(docstring: str) -> str`
### humanize_identifier {#function-humanize-identifier}

> Convert a programming identifier to human-readable text.

Args:
    identifier: Programming identifier (snake_case, camelCase, etc.)
    
Returns:
    Human-readable text

**Signature:** `def humanize_identifier(identifier: str) -> str`
### normalize_line_endings {#function-normalize-line-endings}

> Normalize line endings to Unix-style (LF).

Args:
    text: Text with potentially mixed line endings
    
Returns:
    Text with normalized line endings

**Signature:** `def normalize_line_endings(text: str) -> str`
### count_non_empty_lines {#function-count-non-empty-lines}

> Count non-empty lines in text.

Args:
    text: Text to analyze
    
Returns:
    Number of non-empty lines

**Signature:** `def count_non_empty_lines(text: str) -> int`
### relative_path_to_link {#function-relative-path-to-link}

> Convert a relative file path to an Obsidian-compatible link path.

Args:
    source_path: Path of the source file
    target_path: Path of the target file
    
Returns:
    Relative link path suitable for Obsidian

**Signature:** `def relative_path_to_link(source_path: Path, target_path: Path) -> str`
### format_parameter_list {#function-format-parameter-list}

> Format a list of parameters for display.

Args:
    params: List of (name, type, default) tuples
    
Returns:
    Formatted parameter string

**Signature:** `def format_parameter_list(params: List[Tuple[str, Optional[str], Optional[str]]]) -> str`
### extract_first_paragraph {#function-extract-first-paragraph}

> Extract the first paragraph from text.

Args:
    text: Multi-paragraph text
    
Returns:
    First paragraph only

**Signature:** `def extract_first_paragraph(text: str) -> str`
### format_file_size {#function-format-file-size}

> Format file size in human-readable format.

Args:
    size_bytes: Size in bytes
    
Returns:
    Human-readable size string

**Signature:** `def format_file_size(size_bytes: int) -> str`
