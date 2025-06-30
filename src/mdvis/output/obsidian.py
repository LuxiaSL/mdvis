"""
Obsidian markdown generator with smart cross-references.

Generates clean, navigable markdown documentation optimized for Obsidian
with proper wikilinks, anchors, and cross-references using templates and visualizations.
"""

import asyncio
import aiofiles
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import logging

from ..config.schema import MDVisConfig
from ..models.elements import Module, Class, Function, Parameter, ImportStatement, VisibilityLevel
from ..models.index import CrossReferenceIndex
from .templates import create_template_manager
from .visualizations import create_mermaid_generator

logger = logging.getLogger(__name__)


class ObsidianGenerator:
    """
    Generates Obsidian-compatible markdown documentation with smart linking.
    """
    
    def __init__(self, config: MDVisConfig, index: CrossReferenceIndex):
        """
        Initialize the generator.
        
        Args:
            config: Configuration for output generation
            index: Cross-reference index for smart linking
        """
        self.config = config
        self.index = index
        self._generated_files: Set[Path] = set()
        
        # Initialize template manager and visualization generator
        self.template_manager = create_template_manager(config.verbosity)
        if config.visualization.generate_dependency_graph:
            self.mermaid_generator = create_mermaid_generator(
                index, 
                max_nodes=config.visualization.max_nodes
            )
        else:
            self.mermaid_generator = None
    
    async def generate_documentation(
        self, 
        modules: List[Module], 
        output_root: Path
    ) -> None:
        """
        Generate complete documentation for all modules.
        
        Args:
            modules: List of modules to document
            output_root: Root directory for output
        """
        logger.info(f"Generating Obsidian documentation for {len(modules)} modules")
        
        # Create output directory structure
        await self._setup_output_structure(output_root)
        
        # Generate module documentation concurrently
        semaphore = asyncio.Semaphore(5)  # Limit concurrent file writes
        
        async def generate_module_with_semaphore(module: Module) -> None:
            async with semaphore:
                await self._generate_module_documentation(module, output_root)
        
        # Generate all module docs
        await asyncio.gather(*[
            generate_module_with_semaphore(module) for module in modules
        ])
        
        # Generate dashboard/index
        await self._generate_dashboard(modules, output_root)
        
        # Generate visualizations if enabled
        if self.config.visualization.generate_dependency_graph:
            await self._generate_dependency_visualization(modules, output_root)
        
        # Generate event documentation if enabled
        if self.config.events.enabled and self.index.event_flows:
            await self._generate_event_documentation(output_root)
        
        logger.info(f"Generated {len(self._generated_files)} documentation files")
    
    async def _setup_output_structure(self, output_root: Path) -> None:
        """Setup the output directory structure."""
        output_root.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories if using mirror structure
        if self.config.output.structure == "mirror":
            for module_path in self.index.module_paths.values():
                relative_dir = module_path.parent
                output_dir = output_root / relative_dir
                output_dir.mkdir(parents=True, exist_ok=True)
    
    async def _generate_module_documentation(self, module: Module, output_root: Path) -> None:
        """Generate documentation for a single module."""
        try:
            # Determine output path
            if self.config.output.structure == "mirror":
                # Mirror the source structure
                relative_path = module.file_path.relative_to(module.file_path.parents[len(module.file_path.parents)-1])
                output_path = output_root / relative_path.with_suffix('.md')
            else:
                # Flatten structure
                output_path = output_root / f"{module.name}.md"
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate content
            content = await self._generate_module_content(module)
            
            # Write file
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            self._generated_files.add(output_path)
            logger.debug(f"Generated documentation: {output_path}")
            
        except Exception as e:
            logger.error(f"Error generating documentation for {module.name}: {e}")
    
    async def _generate_module_content(self, module: Module) -> str:
        """Generate the markdown content for a module using templates."""
        try:
            # Use template manager for rendering
            content = self.template_manager.render_module(
                module=module,
                index=self.index,
                config=self.config,
                include_source=self.config.output.include_source,
                source_position=self.config.output.source_position,
                include_private=self.config.output.include_private
            )
            return content
        except Exception as e:
            logger.warning(f"Template rendering failed for {module.name}, using fallback: {e}")
            # Fallback to the original method if template fails
            return await self._generate_module_content_fallback(module)
    
    async def _generate_module_content_fallback(self, module: Module) -> str:
        """Fallback module content generation without templates."""
        lines = []
        
        # Frontmatter
        lines.extend(self._generate_frontmatter(module))
        
        # Title
        lines.append(f"# {module.name}")
        lines.append("")
        
        # Module docstring
        if module.docstring:
            lines.extend(self._format_docstring(module.docstring))
            lines.append("")
        
        # Table of contents (if enabled)
        if self.config.output.generate_toc:
            toc = self._generate_table_of_contents(module)
            if toc:
                lines.extend(toc)
                lines.append("")
        
        # Source code (at top if configured)
        if self.config.output.include_source and self.config.output.source_position == "top":
            lines.extend(self._generate_source_section(module))
            lines.append("")
        
        # Imports
        if module.imports:
            lines.extend(self._generate_imports_section(module))
            lines.append("")
        
        # Classes
        if module.classes:
            lines.append("## Classes")
            lines.append("")
            for cls in module.classes:
                if self._should_include_element(cls.name):
                    lines.extend(self._generate_class_section(cls, module))
                    lines.append("")
        
        # Functions
        if module.functions:
            lines.append("## Functions")
            lines.append("")
            for func in module.functions:
                if self._should_include_element(func.name):
                    lines.extend(self._generate_function_section(func, module))
                    lines.append("")
        
        # TODOs
        if module.todos:
            lines.extend(self._generate_todos_section(module.todos))
            lines.append("")
        
        # Source code (at bottom if configured)
        if self.config.output.include_source and self.config.output.source_position == "bottom":
            lines.extend(self._generate_source_section(module))
        
        return "\n".join(lines)
        """Generate YAML frontmatter for the module."""
        lines = ["---"]
        lines.append(f"title: {module.name}")
        lines.append("type: module")
        lines.append(f"file_path: {module.file_path}")
        
        if module.package:
            lines.append(f"package: {module.package}")
        
        # Statistics
        lines.append("stats:")
        lines.append(f"  classes: {len(module.classes)}")
        lines.append(f"  functions: {len(module.functions)}")
        lines.append(f"  lines_of_code: {module.lines_of_code}")
        lines.append(f"  complexity: {sum(func.complexity for func in module.get_all_functions())}")
        
        # Tags
        tags = ["python", "module"]
        if module.classes:
            tags.append("oop")
        if any(func.is_async for func in module.get_all_functions()):
            tags.append("async")
        if module.event_usage:
            tags.append("events")
        
        lines.append("tags:")
        for tag in tags:
            lines.append(f"  - {tag}")
        
        lines.append("---")
        lines.append("")
        
        return lines
    
    def _generate_table_of_contents(self, module: Module) -> List[str]:
        """Generate table of contents for the module."""
        if self.config.output.toc_style == "collapsible":
            lines = ["<details>", "<summary>Table of Contents</summary>", ""]
        else:
            lines = ["## Table of Contents", ""]
        
        # Add classes
        if module.classes:
            lines.append("### Classes")
            for cls in module.classes:
                if self._should_include_element(cls.name):
                    anchor = cls.get_anchor()
                    lines.append(f"- [[#{anchor}|{cls.name}]]")
            lines.append("")
        
        # Add functions
        if module.functions:
            lines.append("### Functions")
            for func in module.functions:
                if self._should_include_element(func.name):
                    anchor = func.get_anchor()
                    lines.append(f"- [[#{anchor}|{func.name}]]")
            lines.append("")
        
        if self.config.output.toc_style == "collapsible":
            lines.extend(["", "</details>"])
        
        return lines
    
    def _generate_imports_section(self, module: Module) -> List[str]:
        """Generate the imports section."""
        lines = ["## Imports", ""]
        
        for import_stmt in module.imports:
            line = self._format_import_statement(import_stmt, module)
            lines.append(line)
        
        return lines
    
    def _format_import_statement(self, import_stmt: ImportStatement, module: Module) -> str:
        """Format an import statement with smart linking."""
        if import_stmt.module is None:
            # Direct imports: import os, sys
            names = []
            for name, alias in import_stmt.names:
                display_name = alias or name
                # Try to link to internal modules
                if name in self.index.module_paths:
                    names.append(f"[[{name}|{display_name}]]")
                else:
                    names.append(f"`{display_name}`")
            return f"- **import** {', '.join(names)}"
        else:
            # From imports: from module import name
            module_name = import_stmt.module
            module_link = f"[[{module_name}]]" if module_name in self.index.module_paths else f"`{module_name}`"
            
            names = []
            for name, alias in import_stmt.names:
                display_name = alias or name
                # Try to link to specific elements
                element_ref = self.index.resolve_import(name, module.name)
                if element_ref and element_ref.module in self.index.module_paths:
                    names.append(f"[[{element_ref.module}#{element_ref.anchor}|{display_name}]]")
                else:
                    names.append(f"`{display_name}`")
            
            return f"- **from** {module_link} **import** {', '.join(names)}"
    
    def _generate_class_section(self, cls: Class, module: Module) -> List[str]:
        """Generate documentation for a class."""
        lines = []
        
        # Class header
        anchor = cls.get_anchor()
        verbosity = self.config.verbosity
        
        if verbosity == "minimal":
            lines.append(f"### {cls.name}")
        elif verbosity == "standard":
            lines.append(f"### {cls.name} {{#{anchor}}}")
        else:  # detailed
            lines.append(f"### Class: {cls.name} {{#{anchor}}}")
        
        lines.append("")
        
        # Class docstring
        if cls.docstring:
            lines.extend(self._format_docstring(cls.docstring))
            lines.append("")
        
        # Inheritance
        if cls.base_classes:
            base_links = []
            for base_class in cls.base_classes:
                # Try to link to internal base classes
                type_resolution = self.index.resolve_type(base_class, module.name)
                if type_resolution and type_resolution.resolved_to:
                    ref = type_resolution.resolved_to
                    base_links.append(f"[[{ref.module}#{ref.anchor}|{base_class}]]")
                else:
                    base_links.append(f"`{base_class}`")
            
            lines.append(f"**Inherits from:** {', '.join(base_links)}")
            lines.append("")
        
        # Attributes (if any)
        if cls.attributes and verbosity in ("standard", "detailed"):
            lines.append("#### Attributes")
            lines.append("")
            for attr in cls.attributes:
                if self._should_include_element(attr.name):
                    lines.append(self._format_attribute(attr))
            lines.append("")
        
        # Methods
        if cls.methods:
            lines.append("#### Methods")
            lines.append("")
            for method in cls.methods:
                if self._should_include_element(method.name):
                    lines.extend(self._generate_function_section(method, module, is_method=True))
                    lines.append("")
        
        return lines
    
    def _generate_function_section(
        self, 
        func: Function, 
        module: Module, 
        is_method: bool = False
    ) -> List[str]:
        """Generate documentation for a function or method."""
        lines = []
        
        # Function header
        anchor = func.get_anchor()
        verbosity = self.config.verbosity
        
        if verbosity == "minimal":
            title = func.name
        elif verbosity == "standard":
            title = f"{func.name} {{#{anchor}}}"
        else:  # detailed
            prefix = "Method" if is_method else "Function"
            title = f"{prefix}: {func.name} {{#{anchor}}}"
        
        if is_method:
            lines.append(f"##### {title}")
        else:
            lines.append(f"### {title}")
        
        lines.append("")
        
        # Function signature
        if verbosity in ("standard", "detailed"):
            lines.append(f"**Signature:** `{func.signature}`")
            lines.append("")
        
        # Docstring
        if func.docstring:
            lines.extend(self._format_docstring(func.docstring))
            lines.append("")
        
        # Parameters (detailed view)
        if verbosity == "detailed" and func.parameters:
            lines.extend(self._generate_parameters_section(func.parameters, module))
            lines.append("")
        
        # Return type
        if func.return_type and verbosity in ("standard", "detailed"):
            return_link = self._format_type_reference(func.return_type, module)
            lines.append(f"**Returns:** {return_link}")
            lines.append("")
        
        # Decorators
        if func.decorators and verbosity == "detailed":
            lines.append("**Decorators:**")
            for decorator in func.decorators:
                lines.append(f"- `@{decorator.name}`")
            lines.append("")
        
        # Function calls (if present and detailed view)
        if func.calls and verbosity == "detailed":
            lines.append("**Calls:**")
            for call in func.calls[:10]:  # Limit to first 10 calls
                call_link = self._format_call_reference(call, module)
                lines.append(f"- {call_link}")
            if len(func.calls) > 10:
                lines.append(f"- ... and {len(func.calls) - 10} more")
            lines.append("")
        
        return lines
    
    def _generate_parameters_section(self, parameters: List[Parameter], module: Module) -> List[str]:
        """Generate detailed parameters section."""
        lines = ["**Parameters:**", ""]
        
        for param in parameters:
            param_line = f"- **{param.name}**"
            
            # Add type information
            if param.type_ref:
                type_link = self._format_type_reference(param.type_ref, module)
                param_line += f": {type_link}"
            
            # Add default value
            if param.default_value:
                param_line += f" = `{param.default_value}`"
            
            # Add parameter flags
            flags = []
            if param.is_variadic:
                flags.append("*args")
            if param.is_keyword_variadic:
                flags.append("**kwargs")
            if param.is_keyword_only:
                flags.append("keyword-only")
            
            if flags:
                param_line += f" *({', '.join(flags)})*"
            
            lines.append(param_line)
        
        return lines
    
    def _format_attribute(self, attr) -> str:
        """Format an attribute for display."""
        line = f"- **{attr.name}**"
        
        if attr.type_ref:
            line += f": `{attr.type_ref.name}`"
        
        if attr.default_value:
            line += f" = `{attr.default_value}`"
        
        if attr.is_class_var:
            line += " *(class variable)*"
        
        return line
    
    def _format_type_reference(self, type_ref, module: Module) -> str:
        """Format a type reference with smart linking."""
        # Try to resolve the type
        type_resolution = self.index.resolve_type(type_ref.name, module.name)
        
        if type_resolution and type_resolution.resolved_to:
            ref = type_resolution.resolved_to
            return f"[[{ref.module}#{ref.anchor}|{type_ref.name}]]"
        else:
            return f"`{type_ref.name}`"
    
    def _format_call_reference(self, call, module: Module) -> str:
        """Format a function call reference with smart linking."""
        call_resolution = self.index.resolve_call(call.call_chain, module.name)
        
        if call_resolution and call_resolution.resolved_to and not call_resolution.is_external:
            ref = call_resolution.resolved_to
            call_name = ".".join(call.call_chain)
            return f"[[{ref.module}#{ref.anchor}|{call_name}]]"
        else:
            return f"`{'.'.join(call.call_chain)}`"
    
    def _format_docstring(self, docstring: str) -> List[str]:
        """Format a docstring for display."""
        if not docstring:
            return []
        
        lines = ["> [!info] Documentation"]
        for line in docstring.splitlines():
            lines.append(f"> {line}")
        
        return lines
    
    def _generate_source_section(self, module: Module) -> List[str]:
        """Generate the source code section."""
        lines = ["## Source Code", ""]
        
        if module.source_code:
            lines.append("```python")
            lines.append(module.source_code)
            lines.append("```")
        else:
            lines.append("*Source code not available*")
        
        return lines
    
    def _generate_todos_section(self, todos: List[str]) -> List[str]:
        """Generate the TODOs section."""
        lines = ["## TODOs", ""]
        
        for todo in todos:
            lines.append(f"- [ ] {todo}")
        
        return lines
    
    async def _generate_dashboard(self, modules: List[Module], output_root: Path) -> None:
        """Generate the main dashboard/index file."""
        lines = ["# Codebase Documentation", ""]
        
        # Project info
        if self.config.project.name:
            lines.append(f"**Project:** {self.config.project.name}")
        if self.config.project.description:
            lines.append(f"**Description:** {self.config.project.description}")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Statistics
        total_classes = sum(len(module.classes) for module in modules)
        total_functions = sum(len(module.get_all_functions()) for module in modules)
        total_lines = sum(module.lines_of_code for module in modules)
        
        lines.append("## Overview")
        lines.append("")
        lines.append(f"- **Modules:** {len(modules)}")
        lines.append(f"- **Classes:** {total_classes}")
        lines.append(f"- **Functions:** {total_functions}")
        lines.append(f"- **Lines of Code:** {total_lines:,}")
        lines.append("")
        
        # Module index
        lines.append("## Modules")
        lines.append("")
        
        # Group by package if available
        packages = {}
        for module in modules:
            package = module.package or "root"
            if package not in packages:
                packages[package] = []
            packages[package].append(module)
        
        for package, package_modules in sorted(packages.items()):
            if package != "root":
                lines.append(f"### {package}")
                lines.append("")
            
            for module in sorted(package_modules, key=lambda m: m.name):
                module_link = f"[[{module.name}]]"
                stats = f"({len(module.classes)} classes, {len(module.functions)} functions)"
                lines.append(f"- {module_link} {stats}")
            
            lines.append("")
        
        # Write dashboard
        dashboard_path = output_root / "README.md"
        async with aiofiles.open(dashboard_path, 'w', encoding='utf-8') as f:
            await f.write("\n".join(lines))
        
        self._generated_files.add(dashboard_path)
    
    async def _generate_dependency_visualization(self, modules: List[Module], output_root: Path) -> None:
        """Generate dependency visualization using Mermaid diagrams."""
        if not self.mermaid_generator:
            logger.debug("Mermaid generator not available, skipping visualizations")
            return
        
        try:
            # Create visualizations directory
            viz_dir = output_root / "_visualizations"
            viz_dir.mkdir(exist_ok=True)
            
            # Generate dependency graph
            if self.config.visualization.generate_dependency_graph:
                dependency_diagram = self.mermaid_generator.generate_dependency_graph(
                    modules, 
                    exclude_external=self.config.visualization.exclude_external
                )
                
                content = f"""# Module Dependencies

This diagram shows the dependencies between modules in the codebase.

{dependency_diagram}

## Legend

- **Solid arrows** → Import dependencies
- **Dotted arrows** → Inheritance relationships  
- **Bold arrows** → Function call dependencies

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                
                deps_file = viz_dir / "dependencies.md"
                async with aiofiles.open(deps_file, 'w', encoding='utf-8') as f:
                    await f.write(content)
                self._generated_files.add(deps_file)
            
            # Generate class hierarchy if requested
            if self.config.visualization.generate_class_hierarchy:
                hierarchy_diagram = self.mermaid_generator.generate_class_hierarchy(modules)
                
                content = f"""# Class Hierarchy

This diagram shows the inheritance relationships between classes.

{hierarchy_diagram}

## Legend

- **Green boxes** → Data classes
- **Red boxes** → Abstract classes
- **Orange boxes** → Exception classes
- **Gray dashed boxes** → External classes

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                
                hierarchy_file = viz_dir / "class_hierarchy.md"
                async with aiofiles.open(hierarchy_file, 'w', encoding='utf-8') as f:
                    await f.write(content)
                self._generated_files.add(hierarchy_file)
            
            # Generate module overview
            overview_diagram = self.mermaid_generator.generate_module_overview(modules)
            
            content = f"""# Codebase Overview

High-level overview of the codebase structure and organization.

{overview_diagram}

## Statistics

- **Total modules:** {len(modules)}
- **Total classes:** {sum(len(m.classes) for m in modules)}
- **Total functions:** {sum(len(m.get_all_functions()) for m in modules)}
- **Total lines:** {sum(m.lines_of_code for m in modules):,}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            overview_file = viz_dir / "overview.md"
            async with aiofiles.open(overview_file, 'w', encoding='utf-8') as f:
                await f.write(content)
            self._generated_files.add(overview_file)
            
            logger.info(f"Generated {len(self._generated_files & {deps_file, hierarchy_file, overview_file})} visualization files")
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
    
    async def _generate_event_documentation(self, output_root: Path) -> None:
        """Generate event flow documentation with visualizations."""
        if not self.index.event_flows:
            logger.debug("No event flows found, skipping event documentation")
            return
        
        try:
            # Generate event flow diagram
            event_diagram = ""
            if self.mermaid_generator and self.config.visualization.generate_event_flow:
                event_diagram = self.mermaid_generator.generate_event_flow_diagram()
            
            # Create event documentation content
            lines = [
                "# Event System Documentation",
                "",
                "This document describes the event system used throughout the codebase.",
                ""
            ]
            
            if event_diagram:
                lines.extend([
                    "## Event Flow Diagram",
                    "",
                    event_diagram,
                    ""
                ])
            
            # List all events
            lines.extend([
                "## Event Types",
                "",
                f"The system defines {len(self.index.event_flows)} event types:",
                ""
            ])
            
            for event_type, event_flow in self.index.event_flows.items():
                lines.append(f"### `{event_type}`")
                lines.append("")
                
                if event_flow.publishers:
                    lines.append("**Publishers:**")
                    for pub in event_flow.publishers:
                        module_link = f"[[{pub.module}#{pub.anchor}|{pub.name}]]"
                        lines.append(f"- {module_link}")
                    lines.append("")
                
                if event_flow.subscribers:
                    lines.append("**Subscribers:**")
                    for sub in event_flow.subscribers:
                        module_link = f"[[{sub.module}#{sub.anchor}|{sub.name}]]"
                        lines.append(f"- {module_link}")
                    lines.append("")
                
                lines.append(f"*Pattern: {event_flow.pattern_name}*")
                lines.append("")
            
            lines.extend([
                "---",
                f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ])
            
            # Write event documentation
            events_file = output_root / "events.md"
            async with aiofiles.open(events_file, 'w', encoding='utf-8') as f:
                await f.write("\n".join(lines))
            
            self._generated_files.add(events_file)
            logger.info("Generated event documentation")
            
        except Exception as e:
            logger.error(f"Error generating event documentation: {e}")
    
    def _should_include_element(self, name: str) -> bool:
        """Check if an element should be included based on visibility settings."""
        if not self.config.output.include_private:
            if name.startswith('_'):
                return False
        return True