"""
Main documentation processor that orchestrates the entire pipeline.

Coordinates scanning, parsing, analysis, and generation phases to produce
comprehensive documentation with smart cross-references.
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from ..config.schema import MDVisConfig
from ..models.elements import Module
from ..models.index import CrossReferenceIndex
from .scanner import FileScanner, SourceFileInfo, scan_with_metadata
from .parser import EnhancedASTParser
from .indexer import IndexBuilder

logger = logging.getLogger(__name__)


class ProcessingStats:
    """Statistics about the processing pipeline."""
    
    def __init__(self):
        self.files_discovered = 0
        self.files_processed = 0
        self.files_failed = 0
        self.total_lines = 0
        self.modules_created = 0
        self.classes_found = 0
        self.functions_found = 0
        self.imports_resolved = 0
        self.cross_references = 0
        self.processing_time = 0.0
        self.errors: List[str] = []


class DocumentationProcessor:
    """
    Main processor that orchestrates the documentation generation pipeline.
    
    Phases:
    1. Discovery - Find all Python files
    2. Parsing - Parse files into AST and extract structure  
    3. Indexing - Build cross-reference relationships
    4. Analysis - Enhanced analysis (types, async, events)
    5. Generation - Create markdown documentation
    """
    
    def __init__(self, config: MDVisConfig):
        """
        Initialize the processor.
        
        Args:
            config: Configuration for processing
        """
        self.config = config
        self.stats = ProcessingStats()
        self._modules: List[Module] = []
        self._index: Optional[CrossReferenceIndex] = None
        
        # Initialize components
        self._scanner = FileScanner(config.project.exclude_patterns)
        self._parser = EnhancedASTParser(
            event_patterns=[pattern.dict() for pattern in config.events.patterns] if config.events.enabled else []
        )
        self._indexer = IndexBuilder()
    
    async def process_codebase(self, source_root: Path, output_root: Path) -> None:
        """
        Process an entire codebase and generate documentation.
        
        Args:
            source_root: Root directory of source code
            output_root: Root directory for output documentation
        """
        import time
        start_time = time.time()
        
        try:
            logger.info(f"Starting documentation generation for {source_root}")
            
            # Phase 1: Discovery
            await self._phase_discovery(source_root)
            
            # Phase 2: Parsing  
            await self._phase_parsing()
            
            # Phase 3: Indexing
            await self._phase_indexing()
            
            # Phase 4: Analysis (enhanced features)
            await self._phase_analysis()
            
            # Phase 5: Generation
            await self._phase_generation(output_root)
            
            self.stats.processing_time = time.time() - start_time
            
            logger.info(f"Documentation generation complete in {self.stats.processing_time:.2f}s")
            self._log_final_stats()
            
        except Exception as e:
            logger.error(f"Documentation generation failed: {e}")
            raise
    
    async def _phase_discovery(self, source_root: Path) -> List[SourceFileInfo]:
        """Phase 1: Discover all Python files to process."""
        logger.info("Phase 1: Discovering Python files...")
        
        # Build source paths
        source_paths = []
        for path_str in self.config.project.source_paths:
            source_path = source_root / path_str
            if source_path.exists():
                source_paths.append(source_path)
            else:
                logger.warning(f"Source path does not exist: {source_path}")
        
        if not source_paths:
            raise ValueError(f"No valid source paths found in {source_root}")
        
        # Discover files with metadata
        file_infos = await scan_with_metadata(
            source_paths=source_paths,
            exclude_patterns=self.config.project.exclude_patterns,
            max_concurrent=10
        )
        
        self.stats.files_discovered = len(file_infos)
        self.stats.total_lines = sum(info.line_count or 0 for info in file_infos)
        
        logger.info(f"Discovered {len(file_infos)} Python files ({self.stats.total_lines:,} total lines)")
        
        self._file_infos = file_infos
        return file_infos
    
    async def _phase_parsing(self) -> List[Module]:
        """Phase 2: Parse all files into Module objects."""
        logger.info("Phase 2: Parsing Python files...")
        
        # Create semaphore to limit concurrent parsing
        semaphore = asyncio.Semaphore(8)  # Limit concurrent file operations
        
        async def parse_file_with_semaphore(file_info: SourceFileInfo) -> Optional[Module]:
            async with semaphore:
                try:
                    module = await self._parser.parse_file(file_info.path)
                    self.stats.files_processed += 1
                    
                    # Accumulate statistics
                    self.stats.classes_found += len(module.classes)
                    self.stats.functions_found += len(module.get_all_functions())
                    
                    return module
                except Exception as e:
                    self.stats.files_failed += 1
                    error_msg = f"Failed to parse {file_info.path}: {e}"
                    self.stats.errors.append(error_msg)
                    logger.warning(error_msg)
                    return None
        
        # Parse all files concurrently
        parse_tasks = [parse_file_with_semaphore(info) for info in self._file_infos]
        modules = await asyncio.gather(*parse_tasks)
        
        # Filter out failed parses
        self._modules = [module for module in modules if module is not None]
        self.stats.modules_created = len(self._modules)
        
        logger.info(f"Parsed {self.stats.modules_created} modules successfully "
                   f"({self.stats.files_failed} failed)")
        
        return self._modules
    
    async def _phase_indexing(self) -> CrossReferenceIndex:
        """Phase 3: Build cross-reference index."""
        logger.info("Phase 3: Building cross-reference index...")
        
        self._index = await self._indexer.build_index(self._modules)
        
        # Collect indexing stats
        index_stats = self._indexer.get_statistics()
        self.stats.imports_resolved = index_stats['resolved_imports']
        self.stats.cross_references = (
            index_stats['type_resolutions'] + 
            index_stats['call_resolutions']
        )
        
        logger.info(f"Index built: {index_stats['resolved_imports']} imports resolved, "
                   f"{self.stats.cross_references} cross-references found")
        
        return self._index
    
    async def _phase_analysis(self) -> None:
        """Phase 4: Enhanced analysis (types, async patterns, events)."""
        logger.info("Phase 4: Enhanced analysis...")
        
        if not self.config.analysis.detect_async_patterns and not self.config.analysis.detect_type_hints:
            logger.debug("Analysis phase skipped (disabled in config)")
            return
        
        # TODO: Implement enhanced analysis modules
        # - Type hint analysis and linking
        # - Async pattern detection  
        # - Event pattern detection
        # - Complexity analysis
        
        logger.debug("Enhanced analysis complete")
    
    async def _phase_generation(self, output_root: Path) -> None:
        """Phase 5: Generate documentation."""
        logger.info("Phase 5: Generating documentation...")
        
        # Ensure output directory exists
        output_root.mkdir(parents=True, exist_ok=True)
        
        # Import and use the Obsidian generator
        from ..output.obsidian import ObsidianGenerator
        
        generator = ObsidianGenerator(self.config, self._index)
        await generator.generate_documentation(self._modules, output_root)
        
        # Also create a processing status file for debugging
        status_file = output_root / "_processing_status.md"
        await self._write_generation_status(status_file)
        
        logger.info(f"Documentation generated in {output_root}")
    
    async def _write_generation_status(self, status_file: Path) -> None:
        """Write a status file showing what was processed."""
        content = f"""# Documentation Generation Status

Generated on: {self.stats.processing_time:.2f}s

## Statistics

- **Files discovered:** {self.stats.files_discovered}
- **Files processed:** {self.stats.files_processed}  
- **Files failed:** {self.stats.files_failed}
- **Total lines:** {self.stats.total_lines:,}
- **Modules created:** {self.stats.modules_created}
- **Classes found:** {self.stats.classes_found}
- **Functions found:** {self.stats.functions_found}
- **Imports resolved:** {self.stats.imports_resolved}
- **Cross-references:** {self.stats.cross_references}

## Configuration

- **Verbosity:** {self.config.verbosity}
- **Include private:** {self.config.output.include_private}
- **Events enabled:** {self.config.events.enabled}
- **Generate diagrams:** {self.config.visualization.generate_dependency_graph}

## Modules Processed

"""
        
        for module in self._modules:
            content += f"- **{module.name}** ({len(module.classes)} classes, {len(module.functions)} functions)\n"
        
        if self.stats.errors:
            content += "\n## Errors\n\n"
            for error in self.stats.errors:
                content += f"- {error}\n"
        
        # Write the file
        import aiofiles
        async with aiofiles.open(status_file, 'w', encoding='utf-8') as f:
            await f.write(content)
    
    def _log_final_stats(self) -> None:
        """Log final processing statistics."""
        logger.info("=== Final Processing Statistics ===")
        logger.info(f"Files discovered: {self.stats.files_discovered}")
        logger.info(f"Files processed: {self.stats.files_processed}")
        logger.info(f"Files failed: {self.stats.files_failed}")
        logger.info(f"Total lines: {self.stats.total_lines:,}")
        logger.info(f"Modules created: {self.stats.modules_created}")
        logger.info(f"Classes found: {self.stats.classes_found}")
        logger.info(f"Functions found: {self.stats.functions_found}")
        logger.info(f"Imports resolved: {self.stats.imports_resolved}")
        logger.info(f"Cross-references: {self.stats.cross_references}")
        logger.info(f"Processing time: {self.stats.processing_time:.2f}s")
        
        if self.stats.errors:
            logger.warning(f"Errors encountered: {len(self.stats.errors)}")
            for error in self.stats.errors[:5]:  # Show first 5 errors
                logger.warning(f"  - {error}")
            if len(self.stats.errors) > 5:
                logger.warning(f"  ... and {len(self.stats.errors) - 5} more")
    
    # Public API for accessing results
    
    @property
    def modules(self) -> List[Module]:
        """Get the processed modules."""
        return self._modules
    
    @property
    def index(self) -> Optional[CrossReferenceIndex]:
        """Get the cross-reference index."""
        return self._index
    
    def get_module_by_name(self, name: str) -> Optional[Module]:
        """Get a module by name."""
        for module in self._modules:
            if module.name == name:
                return module
        return None
    
    def get_modules_by_package(self, package: str) -> List[Module]:
        """Get all modules in a package."""
        return [module for module in self._modules if module.package == package]
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get a summary of processing results."""
        return {
            'stats': {
                'files_discovered': self.stats.files_discovered,
                'files_processed': self.stats.files_processed,
                'files_failed': self.stats.files_failed,
                'total_lines': self.stats.total_lines,
                'modules_created': self.stats.modules_created,
                'classes_found': self.stats.classes_found,
                'functions_found': self.stats.functions_found,
                'imports_resolved': self.stats.imports_resolved,
                'cross_references': self.stats.cross_references,
                'processing_time': self.stats.processing_time
            },
            'config': {
                'verbosity': self.config.verbosity,
                'include_private': self.config.output.include_private,
                'events_enabled': self.config.events.enabled,
                'source_paths': self.config.project.source_paths,
                'exclude_patterns': self.config.project.exclude_patterns
            },
            'modules': [
                {
                    'name': module.name,
                    'package': module.package,
                    'classes': len(module.classes),
                    'functions': len(module.functions),
                    'lines_of_code': module.lines_of_code
                }
                for module in self._modules
            ],
            'errors': self.stats.errors
        }