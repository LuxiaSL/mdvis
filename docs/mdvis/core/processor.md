# processor

> Main documentation processor that orchestrates the entire pipeline.

Coordinates scanning, parsing, analysis, and generation phases to produce
comprehensive documentation with smart cross-references.

## Overview

- **Classes:** 2
- **Functions:** 0
- **Lines of Code:** 377

## Imports
- **import** `asyncio`
- **from** `pathlib` **import** `Path`
- **from** `typing` **import** `List, Dict, Any, Optional, Callable, Awaitable`
- **import** `logging`
- **from** `config.schema` **import** `MDVisConfig`
- **from** `models.elements` **import** `Module`
- **from** `models.index` **import** `CrossReferenceIndex`
- **from** `scanner` **import** `FileScanner, SourceFileInfo, scan_with_metadata`
- **from** `parser` **import** `EnhancedASTParser`
- **from** `indexer` **import** `IndexBuilder`

## Classes
### ProcessingStats {#class-processingstats}

> Statistics about the processing pipeline.


#### Methods
##### __init__ {#method-init}


**Signature:** `def __init__(self)`
### DocumentationProcessor {#class-documentationprocessor}

> Main processor that orchestrates the documentation generation pipeline.

Phases:
1. Discovery - Find all Python files
2. Parsing - Parse files into AST and extract structure  
3. Indexing - Build cross-reference relationships
4. Analysis - Enhanced analysis (types, async, events)
5. Generation - Create markdown documentation


#### Methods
##### __init__ {#method-init}

> Initialize the processor.

**Signature:** `def __init__(self, config: MDVisConfig)`
##### process_codebase {#method-process-codebase}

> Process an entire codebase and generate documentation.

**Signature:** `async def process_codebase(self, source_root: Path, output_root: Path, progress_callback: Optional[ProgressCallback] = None) -> None`
##### _phase_discovery {#method-phase-discovery}

> Phase 1: Discover all Python files to process..

**Signature:** `async def _phase_discovery(self, source_root: Path) -> List[SourceFileInfo]`
##### _phase_parsing {#method-phase-parsing}

> Phase 2: Parse all files into Module objects..

**Signature:** `async def _phase_parsing(self) -> List[Module]`
##### _phase_indexing {#method-phase-indexing}

> Phase 3: Build cross-reference index..

**Signature:** `async def _phase_indexing(self) -> CrossReferenceIndex`
##### _phase_analysis {#method-phase-analysis}

> Phase 4: Enhanced analysis (types, async patterns, events)..

**Signature:** `async def _phase_analysis(self) -> None`
##### _phase_generation {#method-phase-generation}

> Phase 5: Generate documentation..

**Signature:** `async def _phase_generation(self, output_root: Path) -> None`
##### _write_generation_status {#method-write-generation-status}

> Write a status file showing what was processed..

**Signature:** `async def _write_generation_status(self, status_file: Path) -> None`
##### _log_final_stats {#method-log-final-stats}

> Log final processing statistics..

**Signature:** `def _log_final_stats(self) -> None`
##### modules {#method-modules}

> Get the processed modules..

**Signature:** `def modules(self) -> List[Module]`
##### index {#method-index}

> Get the cross-reference index..

**Signature:** `def index(self) -> Optional[CrossReferenceIndex]`
##### get_module_by_name {#method-get-module-by-name}

> Get a module by name..

**Signature:** `def get_module_by_name(self, name: str) -> Optional[Module]`
##### get_modules_by_package {#method-get-modules-by-package}

> Get all modules in a package..

**Signature:** `def get_modules_by_package(self, package: str) -> List[Module]`
##### get_processing_summary {#method-get-processing-summary}

> Get a summary of processing results..

**Signature:** `def get_processing_summary(self) -> Dict[str, Any]`

