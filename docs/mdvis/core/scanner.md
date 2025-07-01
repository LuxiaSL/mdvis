# scanner

> Async file scanner for discovering Python source files.

Efficiently scans directories while respecting gitignore patterns and exclusions.

## Overview

- **Classes:** 2
- **Functions:** 2
- **Lines of Code:** 305

## Imports
- **import** `asyncio`
- **import** `aiofiles`
- **from** `pathlib` **import** `Path`
- **from** `typing` **import** `List, Set, Optional, AsyncGenerator`
- **import** `pathspec`
- **import** `logging`
- **from** `models.elements` **import** `Location`

## Classes
### FileScanner {#class-filescanner}

> Async file scanner that discovers Python files while respecting exclusion patterns.


#### Methods
##### __init__ {#method-init}

> Initialize the scanner.

**Signature:** `def __init__(self, exclude_patterns: Optional[List[str]] = None)`
##### _setup_pathspec {#method-setup-pathspec}

> Setup pathspec for pattern matching..

**Signature:** `def _setup_pathspec(self) -> None`
##### discover_python_files {#method-discover-python-files}

> Discover all Python files in the given source paths.

**Signature:** `async def discover_python_files(self, source_paths: List[Path], load_gitignore: bool = True) -> List[Path]`
##### _load_gitignore_patterns {#method-load-gitignore-patterns}

> Load .gitignore patterns from source directories..

**Signature:** `async def _load_gitignore_patterns(self, source_paths: List[Path]) -> None`
##### _scan_directory {#method-scan-directory}

> Recursively scan a directory for Python files.

**Signature:** `async def _scan_directory(self, directory: Path) -> AsyncGenerator[Path, None]`
##### _is_python_file {#method-is-python-file}

> Check if a file is a Python source file..

**Signature:** `def _is_python_file(self, path: Path) -> bool`
##### _is_excluded {#method-is-excluded}

> Check if a path should be excluded based on patterns..

**Signature:** `def _is_excluded(self, path: Path) -> bool`
### SourceFileInfo {#class-sourcefileinfo}

> Information about a discovered source file.


#### Methods
##### __init__ {#method-init}


**Signature:** `def __init__(self, path: Path)`
##### load_metadata {#method-load-metadata}

> Load file metadata asynchronously..

**Signature:** `async def load_metadata(self) -> None`
##### _detect_encoding_and_count_lines {#method-detect-encoding-and-count-lines}

> Detect file encoding and count lines..

**Signature:** `async def _detect_encoding_and_count_lines(self) -> None`

## Functions
### scan_with_metadata {#function-scan-with-metadata}

> Scan for Python files and load their metadata concurrently.

Args:
    source_paths: List of source directories/files to scan
    exclude_patterns: List of exclusion patterns
    max_concurrent: Maximum number of concurrent file operations
    
Returns:
    List of SourceFileInfo objects with loaded metadata

**Signature:** `async def scan_with_metadata(source_paths: List[Path], exclude_patterns: Optional[List[str]] = None, max_concurrent: int = 10) -> List[SourceFileInfo]`
### get_file_stats {#function-get-file-stats}

> Get statistics about Python files in the source paths.

Args:
    source_paths: List of source directories/files to scan
    exclude_patterns: List of exclusion patterns
    
Returns:
    Dictionary with file statistics

**Signature:** `async def get_file_stats(source_paths: List[Path], exclude_patterns: Optional[List[str]] = None) -> dict`
