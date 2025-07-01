---
title: scanner
type: module
file_path: /home/luxia/projects/mdvis/src/mdvis/core/scanner.py
package: mdvis.core
stats:
  classes: 2
  functions: 2
  lines_of_code: 305
  complexity: 40
tags:
  - python
  - module
  - oop
  - async
---

# scanner

> [!info] Documentation
> Async file scanner for discovering Python source files.
> 
> Efficiently scans directories while respecting gitignore patterns and exclusions.

## Table of Contents

### Classes
- [[#class-filescanner|FileScanner]]
- [[#class-sourcefileinfo|SourceFileInfo]]

### Functions
- [[#function-scan-with-metadata|scan_with_metadata]]
- [[#function-get-file-stats|get_file_stats]]


## Imports

- **import** `asyncio`
- **import** `aiofiles`
- **from** `pathlib` **import** `Path`
- **from** `typing` **import** `List`, `Set`, `Optional`, `AsyncGenerator`
- **import** `pathspec`
- **import** `logging`
- **from** `models.elements` **import** [[elements#class-location|Location]]

## Classes

### FileScanner {#class-filescanner}

> [!info] Documentation
> Async file scanner that discovers Python files while respecting exclusion patterns.

#### Methods

##### discover_python_files {#method-discover-python-files}

**Signature:** `async def discover_python_files(self, source_paths: List[Path], load_gitignore: bool = True) -> List[Path]`

> [!info] Documentation
> Discover all Python files in the given source paths.
> 
> Args:
>     source_paths: List of source directories/files to scan
>     load_gitignore: Whether to load and respect .gitignore files
>     
> Returns:
>     List of Python file paths found

**Returns:** `List[Path]`



### SourceFileInfo {#class-sourcefileinfo}

> [!info] Documentation
> Information about a discovered source file.

#### Methods

##### load_metadata {#method-load-metadata}

**Signature:** `async def load_metadata(self) -> None`

> [!info] Documentation
> Load file metadata asynchronously.

**Returns:** `None`



## Functions

### scan_with_metadata {#function-scan-with-metadata}

**Signature:** `async def scan_with_metadata(source_paths: List[Path], exclude_patterns: Optional[List[str]] = None, max_concurrent: int = 10) -> List[SourceFileInfo]`

> [!info] Documentation
> Scan for Python files and load their metadata concurrently.
> 
> Args:
>     source_paths: List of source directories/files to scan
>     exclude_patterns: List of exclusion patterns
>     max_concurrent: Maximum number of concurrent file operations
>     
> Returns:
>     List of SourceFileInfo objects with loaded metadata

**Returns:** `List[SourceFileInfo]`


### get_file_stats {#function-get-file-stats}

**Signature:** `async def get_file_stats(source_paths: List[Path], exclude_patterns: Optional[List[str]] = None) -> dict`

> [!info] Documentation
> Get statistics about Python files in the source paths.
> 
> Args:
>     source_paths: List of source directories/files to scan
>     exclude_patterns: List of exclusion patterns
>     
> Returns:
>     Dictionary with file statistics

**Returns:** `dict`


## Source Code

```python
"""
Async file scanner for discovering Python source files.

Efficiently scans directories while respecting gitignore patterns and exclusions.
"""

import asyncio
import aiofiles
from pathlib import Path
from typing import List, Set, Optional, AsyncGenerator
import pathspec
import logging

from ..models.elements import Location

logger = logging.getLogger(__name__)


class FileScanner:
    """
    Async file scanner that discovers Python files while respecting exclusion patterns.
    """
    
    def __init__(self, exclude_patterns: Optional[List[str]] = None):
        """
        Initialize the scanner.
        
        Args:
            exclude_patterns: List of gitignore-style patterns to exclude
        """
        self.exclude_patterns = exclude_patterns or []
        self._pathspec: Optional[pathspec.PathSpec] = None
        self._setup_pathspec()
    
    def _setup_pathspec(self) -> None:
        """Setup pathspec for pattern matching."""
        if self.exclude_patterns:
            self._pathspec = pathspec.PathSpec.from_lines('gitignore', self.exclude_patterns)
        else:
            self._pathspec = pathspec.PathSpec.from_lines('gitignore', [])
    
    async def discover_python_files(
        self, 
        source_paths: List[Path],
        load_gitignore: bool = True
    ) -> List[Path]:
        """
        Discover all Python files in the given source paths.
        
        Args:
            source_paths: List of source directories/files to scan
            load_gitignore: Whether to load and respect .gitignore files
            
        Returns:
            List of Python file paths found
        """
        logger.info(f"Scanning {len(source_paths)} source paths for Python files")
        
        # Load gitignore patterns if requested
        if load_gitignore:
            await self._load_gitignore_patterns(source_paths)
        
        # Collect all Python files
        all_files = []
        
        for source_path in source_paths:
            if source_path.is_file():
                if self._is_python_file(source_path) and not self._is_excluded(source_path):
                    all_files.append(source_path)
            elif source_path.is_dir():
                async for file_path in self._scan_directory(source_path):
                    all_files.append(file_path)
            else:
                logger.warning(f"Source path does not exist: {source_path}")
        
        logger.info(f"Found {len(all_files)} Python files")
        return sorted(all_files)  # Sort for consistent ordering
    
    async def _load_gitignore_patterns(self, source_paths: List[Path]) -> None:
        """Load .gitignore patterns from source directories."""
        gitignore_patterns = list(self.exclude_patterns)  # Start with configured patterns
        
        # Find all .gitignore files in source paths
        gitignore_files = []
        for source_path in source_paths:
            if source_path.is_dir():
                # Look for .gitignore in this directory and parent directories
                current_dir = source_path
                while current_dir != current_dir.parent:  # Stop at filesystem root
                    gitignore_file = current_dir / '.gitignore'
                    if gitignore_file.exists():
                        gitignore_files.append(gitignore_file)
                        break  # Only use the closest .gitignore
                    current_dir = current_dir.parent
        
        # Load patterns from .gitignore files
        for gitignore_file in gitignore_files:
            try:
                async with aiofiles.open(gitignore_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    lines = content.splitlines()
                    # Filter out comments and empty lines
                    patterns = [
                        line.strip() for line in lines 
                        if line.strip() and not line.strip().startswith('#')
                    ]
                    gitignore_patterns.extend(patterns)
                    logger.debug(f"Loaded {len(patterns)} patterns from {gitignore_file}")
            except Exception as e:
                logger.warning(f"Error reading {gitignore_file}: {e}")
        
        # Update pathspec with all patterns
        if gitignore_patterns:
            self._pathspec = pathspec.PathSpec.from_lines('gitignore', gitignore_patterns)
            logger.debug(f"Using {len(gitignore_patterns)} exclusion patterns")
    
    async def _scan_directory(self, directory: Path) -> AsyncGenerator[Path, None]:
        """
        Recursively scan a directory for Python files.
        
        Args:
            directory: Directory to scan
            
        Yields:
            Python file paths
        """
        try:
            # Use asyncio to scan directory without blocking
            entries = await asyncio.to_thread(list, directory.rglob('*.py'))
            
            for entry in entries:
                if entry.is_file() and not self._is_excluded(entry):
                    yield entry
                    
        except PermissionError:
            logger.warning(f"Permission denied scanning directory: {directory}")
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
    
    def _is_python_file(self, path: Path) -> bool:
        """Check if a file is a Python source file."""
        return path.suffix == '.py' and path.is_file()
    
    def _is_excluded(self, path: Path) -> bool:
        """Check if a path should be excluded based on patterns."""
        if not self._pathspec:
            return False
        
        # Convert to relative path for pattern matching
        try:
            # Try to get relative path from current working directory
            relative_path = path.relative_to(Path.cwd())
        except ValueError:
            # If path is not relative to cwd, use the path as-is
            relative_path = path
        
        return self._pathspec.match_file(str(relative_path))


class SourceFileInfo:
    """Information about a discovered source file."""
    
    def __init__(self, path: Path):
        self.path = path
        self.size: Optional[int] = None
        self.encoding: str = 'utf-8'
        self.line_count: Optional[int] = None
        self.is_readable: bool = True
        self.error: Optional[str] = None
    
    async def load_metadata(self) -> None:
        """Load file metadata asynchronously."""
        try:
            # Get file size
            stat_result = await asyncio.to_thread(self.path.stat)
            self.size = stat_result.st_size
            
            # Detect encoding and count lines
            await self._detect_encoding_and_count_lines()
            
        except Exception as e:
            self.is_readable = False
            self.error = str(e)
            logger.warning(f"Error loading metadata for {self.path}: {e}")
    
    async def _detect_encoding_and_count_lines(self) -> None:
        """Detect file encoding and count lines."""
        try:
            # Try UTF-8 first (most common)
            async with aiofiles.open(self.path, 'r', encoding='utf-8') as f:
                content = await f.read()
                self.line_count = content.count('\n') + 1
                self.encoding = 'utf-8'
                return
        except UnicodeDecodeError:
            pass
        
        # Try other common encodings
        for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
            try:
                async with aiofiles.open(self.path, 'r', encoding=encoding) as f:
                    content = await f.read()
                    self.line_count = content.count('\n') + 1
                    self.encoding = encoding
                    return
            except UnicodeDecodeError:
                continue
        
        # If all else fails, use binary mode to count lines
        try:
            async with aiofiles.open(self.path, 'rb') as f:
                content = await f.read()
                self.line_count = content.count(b'\n') + 1
                self.encoding = 'utf-8'  # Default assumption
        except Exception as e:
            logger.warning(f"Could not count lines in {self.path}: {e}")
            self.line_count = 0


async def scan_with_metadata(
    source_paths: List[Path],
    exclude_patterns: Optional[List[str]] = None,
    max_concurrent: int = 10
) -> List[SourceFileInfo]:
    """
    Scan for Python files and load their metadata concurrently.
    
    Args:
        source_paths: List of source directories/files to scan
        exclude_patterns: List of exclusion patterns
        max_concurrent: Maximum number of concurrent file operations
        
    Returns:
        List of SourceFileInfo objects with loaded metadata
    """
    scanner = FileScanner(exclude_patterns)
    file_paths = await scanner.discover_python_files(source_paths)
    
    # Create SourceFileInfo objects
    file_infos = [SourceFileInfo(path) for path in file_paths]
    
    # Load metadata concurrently with semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def load_metadata_with_semaphore(file_info: SourceFileInfo) -> SourceFileInfo:
        async with semaphore:
            await file_info.load_metadata()
            return file_info
    
    # Process all files concurrently
    if file_infos:
        logger.info(f"Loading metadata for {len(file_infos)} files...")
        file_infos = await asyncio.gather(*[
            load_metadata_with_semaphore(info) for info in file_infos
        ])
    
    # Filter out unreadable files
    readable_files = [info for info in file_infos if info.is_readable]
    if len(readable_files) != len(file_infos):
        skipped = len(file_infos) - len(readable_files)
        logger.warning(f"Skipped {skipped} unreadable files")
    
    return readable_files


async def get_file_stats(source_paths: List[Path], exclude_patterns: Optional[List[str]] = None) -> dict:
    """
    Get statistics about Python files in the source paths.
    
    Args:
        source_paths: List of source directories/files to scan
        exclude_patterns: List of exclusion patterns
        
    Returns:
        Dictionary with file statistics
    """
    file_infos = await scan_with_metadata(source_paths, exclude_patterns)
    
    total_files = len(file_infos)
    total_size = sum(info.size or 0 for info in file_infos)
    total_lines = sum(info.line_count or 0 for info in file_infos)
    
    # Group by directory
    directories = {}
    for info in file_infos:
        dir_path = info.path.parent
        if dir_path not in directories:
            directories[dir_path] = {'files': 0, 'lines': 0, 'size': 0}
        directories[dir_path]['files'] += 1
        directories[dir_path]['lines'] += info.line_count or 0
        directories[dir_path]['size'] += info.size or 0
    
    return {
        'total_files': total_files,
        'total_size_bytes': total_size,
        'total_lines': total_lines,
        'average_file_size': total_size / total_files if total_files > 0 else 0,
        'average_lines_per_file': total_lines / total_files if total_files > 0 else 0,
        'directories': {str(k): v for k, v in directories.items()},
        'readable_files': len([info for info in file_infos if info.is_readable]),
        'encoding_distribution': {
            encoding: len([info for info in file_infos if info.encoding == encoding])
            for encoding in set(info.encoding for info in file_infos)
        }
    }
```