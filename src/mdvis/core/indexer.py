"""
Cross-reference index builder for smart linking and navigation.

Builds a comprehensive index of relationships between code elements
to enable smart cross-referencing in generated documentation.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
import logging

from ..models.elements import Module, Class, Function, ImportStatement
from ..models.index import (
    CrossReferenceIndex, ElementRef, ImportResolution, TypeResolution, 
    CallResolution, DependencyEdge, ReferenceType, EventFlow
)

logger = logging.getLogger(__name__)


class IndexBuilder:
    """
    Builds cross-reference indexes from parsed modules.
    
    This is the heart of smart linking - it analyzes all relationships
    between code elements to enable proper cross-references.
    """
    
    def __init__(self):
        self.index = CrossReferenceIndex()
        self._module_map: Dict[str, Module] = {}
        self._builtin_types = {
            'int', 'str', 'bool', 'float', 'list', 'dict', 'tuple', 'set', 'frozenset',
            'bytes', 'bytearray', 'memoryview', 'complex', 'object', 'type', 'None'
        }
        self._typing_types = {
            'List', 'Dict', 'Tuple', 'Set', 'FrozenSet', 'Optional', 'Union', 'Any',
            'Callable', 'Iterable', 'Iterator', 'Generator', 'Coroutine', 'Awaitable',
            'AsyncIterable', 'AsyncIterator', 'AsyncGenerator', 'Type', 'TypeVar',
            'Generic', 'Protocol', 'Literal', 'Final', 'ClassVar'
        }
    
    async def build_index(self, modules: List[Module]) -> CrossReferenceIndex:
        """
        Build comprehensive cross-reference index from modules.
        
        Args:
            modules: List of parsed modules
            
        Returns:
            Complete cross-reference index
        """
        logger.info(f"Building cross-reference index for {len(modules)} modules")
        
        # Store modules for reference resolution
        self._module_map = {module.name: module for module in modules}
        
        # Phase 1: Register all elements
        for module in modules:
            self.index.register_module(module)
        
        # Phase 2: Resolve imports
        await self._resolve_imports(modules)
        
        # Phase 3: Resolve type references
        await self._resolve_type_references(modules)
        
        # Phase 4: Resolve function/method calls
        await self._resolve_call_references(modules)
        
        # Phase 5: Build dependency graph
        await self._build_dependency_graph(modules)
        
        # Phase 6: Extract event flows
        await self._extract_event_flows(modules)
        
        logger.info(f"Index built: {len(self.index.functions)} functions, "
                   f"{len(self.index.classes)} classes, "
                   f"{len(self.index.module_dependencies)} dependencies")
        
        return self.index
    
    async def _resolve_imports(self, modules: List[Module]) -> None:
        """Resolve import statements to their target elements."""
        logger.debug("Resolving import statements...")
        
        for module in modules:
            for import_stmt in module.imports:
                resolution = await self._resolve_single_import(import_stmt, module)
                if resolution:
                    self.index.import_resolutions.append(resolution)
                else:
                    # Track unresolved imports
                    import_name = import_stmt.module or ', '.join([name for name, _ in import_stmt.names])
                    self.index.unresolved_imports.append(import_name)
    
    async def _resolve_single_import(
        self, 
        import_stmt: ImportStatement, 
        from_module: Module
    ) -> Optional[ImportResolution]:
        """Resolve a single import statement."""
        targets = []
        
        if import_stmt.module is None:
            # Direct imports: import os, sys
            for name, alias in import_stmt.names:
                if name in self.index.module_paths:
                    # Internal module import
                    target = ElementRef(
                        name=alias or name,
                        module=name,
                        element_type="module",
                        anchor=f"module-{name}",
                        file_path=self.index.module_paths[name]
                    )
                    targets.append(target)
                    
                    # Add dependency
                    self.index.add_dependency(
                        from_module.name, name, ReferenceType.IMPORT, f"import {name}"
                    )
        else:
            # From imports: from module import name
            module_name = import_stmt.module
            
            # Handle relative imports
            if import_stmt.is_relative:
                module_name = self._resolve_relative_import(
                    import_stmt.module, import_stmt.level, from_module
                )
            
            if module_name and module_name in self._module_map:
                target_module = self._module_map[module_name]
                
                for name, alias in import_stmt.names:
                    target = self._find_element_in_module(name, target_module)
                    if target:
                        # Update the name to use alias if provided
                        target.name = alias or name
                        targets.append(target)
                
                # Add dependency
                self.index.add_dependency(
                    from_module.name, module_name, ReferenceType.IMPORT, 
                    f"from {import_stmt.module} import {', '.join([name for name, _ in import_stmt.names])}"
                )
        
        if targets:
            return ImportResolution(
                original_import=self._import_to_string(import_stmt),
                resolved_module=import_stmt.module or "builtin",
                imported_names=[alias or name for name, alias in import_stmt.names],
                is_internal=any(target.module in self._module_map for target in targets),
                targets=targets
            )
        
        return None
    
    def _resolve_relative_import(
        self, 
        module_name: Optional[str], 
        level: int, 
        from_module: Module
    ) -> Optional[str]:
        """Resolve relative import to absolute module name."""
        if not from_module.package:
            return module_name
        
        # Split package into parts
        package_parts = from_module.package.split('.')
        
        # Go up the specified number of levels
        if level > len(package_parts):
            return None  # Invalid relative import
        
        base_package_parts = package_parts[:-level] if level > 0 else package_parts
        
        if module_name:
            # from ..module import something
            return '.'.join(base_package_parts + [module_name])
        else:
            # from .. import something
            return '.'.join(base_package_parts)
    
    def _find_element_in_module(self, name: str, module: Module) -> Optional[ElementRef]:
        """Find a named element within a module."""
        # Check functions
        for func in module.functions:
            if func.name == name:
                return ElementRef(
                    name=name,
                    module=module.name,
                    element_type="function",
                    anchor=func.get_anchor(),
                    file_path=module.file_path,
                    location=func.location
                )
        
        # Check classes
        for cls in module.classes:
            if cls.name == name:
                return ElementRef(
                    name=name,
                    module=module.name,
                    element_type="class",
                    anchor=cls.get_anchor(),
                    file_path=module.file_path,
                    location=cls.location
                )
            
            # Check methods within classes
            for method in cls.methods:
                if method.name == name:
                    return ElementRef(
                        name=name,
                        module=module.name,
                        element_type="method",
                        anchor=method.get_anchor(),
                        file_path=module.file_path,
                        location=method.location,
                        parent=cls.name
                    )
        
        # Check module-level attributes
        for attr in module.attributes:
            if attr.name == name:
                return ElementRef(
                    name=name,
                    module=module.name,
                    element_type="attribute",
                    anchor=f"attribute-{name}",
                    file_path=module.file_path,
                    location=attr.location
                )
        
        return None
    
    async def _resolve_type_references(self, modules: List[Module]) -> None:
        """Resolve type annotations to their definitions."""
        logger.debug("Resolving type references...")
        
        for module in modules:
            # Resolve type references in functions
            for func in module.get_all_functions():
                await self._resolve_function_types(func, module)
            
            # Resolve type references in classes
            for cls in module.classes:
                await self._resolve_class_types(cls, module)
    
    async def _resolve_function_types(self, func: Function, module: Module) -> None:
        """Resolve type references in a function."""
        # Resolve parameter types
        for param in func.parameters:
            if param.type_ref:
                resolution = await self._resolve_type_name(param.type_ref.name, module)
                if resolution:
                    self.index.type_resolutions[f"{module.name}.{func.name}.{param.name}"] = resolution
        
        # Resolve return type
        if func.return_type:
            resolution = await self._resolve_type_name(func.return_type.name, module)
            if resolution:
                self.index.type_resolutions[f"{module.name}.{func.name}.return"] = resolution
    
    async def _resolve_class_types(self, cls: Class, module: Module) -> None:
        """Resolve type references in a class."""
        # Resolve base classes
        for base_class in cls.base_classes:
            resolution = await self._resolve_type_name(base_class, module)
            if resolution:
                self.index.type_resolutions[f"{module.name}.{cls.name}.base.{base_class}"] = resolution
                
                # Add inheritance dependency
                if resolution.resolved_to:
                    self.index.add_dependency(
                        module.name, resolution.resolved_to.module,
                        ReferenceType.INHERITANCE, f"{cls.name} inherits from {base_class}"
                    )
        
        # Resolve attribute types
        for attr in cls.attributes:
            if attr.type_ref:
                resolution = await self._resolve_type_name(attr.type_ref.name, module)
                if resolution:
                    self.index.type_resolutions[f"{module.name}.{cls.name}.{attr.name}"] = resolution
    
    async def _resolve_type_name(self, type_name: str, context_module: Module) -> Optional[TypeResolution]:
        """Resolve a type name to its definition."""
        # Handle generic types like List[str]
        base_type = type_name.split('[')[0] if '[' in type_name else type_name
        
        # Check if it's a builtin type
        if base_type in self._builtin_types:
            return TypeResolution(type_name=type_name, is_builtin=True)
        
        # Check if it's a typing module type
        if base_type in self._typing_types:
            return TypeResolution(type_name=type_name, is_external=True)
        
        # Try to find in current module first
        element = self._find_element_in_module(base_type, context_module)
        if element and element.element_type == "class":
            return TypeResolution(type_name=type_name, resolved_to=element)
        
        # Try to find in other modules
        for module_name, module in self._module_map.items():
            element = self._find_element_in_module(base_type, module)
            if element and element.element_type == "class":
                return TypeResolution(type_name=type_name, resolved_to=element)
        
        # Assume it's external if not found
        return TypeResolution(type_name=type_name, is_external=True)
    
    async def _resolve_call_references(self, modules: List[Module]) -> None:
        """Resolve function/method calls to their targets."""
        logger.debug("Resolving call references...")
        
        for module in modules:
            for func in module.get_all_functions():
                for call in func.calls:
                    resolution = await self._resolve_call(call.call_chain, module)
                    if resolution:
                        self.index.call_resolutions.append(resolution)
    
    async def _resolve_call(self, call_chain: List[str], context_module: Module) -> Optional[CallResolution]:
        """Resolve a function call to its target."""
        if not call_chain:
            return None
        
        # Simple function call
        if len(call_chain) == 1:
            func_name = call_chain[0]
            
            # Try current module first
            element = self._find_element_in_module(func_name, context_module)
            if element and element.element_type in ("function", "method"):
                return CallResolution(
                    call_chain=call_chain,
                    resolved_to=element,
                    confidence=1.0
                )
            
            # Try other modules
            for module in self._module_map.values():
                element = self._find_element_in_module(func_name, module)
                if element and element.element_type in ("function", "method"):
                    return CallResolution(
                        call_chain=call_chain,
                        resolved_to=element,
                        confidence=0.8
                    )
        
        # Method call (obj.method)
        elif len(call_chain) >= 2:
            # Try to resolve as class method
            obj_name, method_name = call_chain[0], call_chain[1]
            
            # Look for class in current module
            for cls in context_module.classes:
                if cls.name == obj_name:
                    for method in cls.methods:
                        if method.name == method_name:
                            return CallResolution(
                                call_chain=call_chain,
                                resolved_to=ElementRef(
                                    name=method_name,
                                    module=context_module.name,
                                    element_type="method",
                                    anchor=method.get_anchor(),
                                    file_path=context_module.file_path,
                                    location=method.location,
                                    parent=cls.name
                                ),
                                confidence=0.9
                            )
        
        # External or unresolved call
        return CallResolution(
            call_chain=call_chain,
            is_external=True,
            confidence=0.1
        )
    
    async def _build_dependency_graph(self, modules: List[Module]) -> None:
        """Build the module dependency graph."""
        logger.debug("Building dependency graph...")
        
        # Dependencies are already added during import resolution
        # Here we can add additional dependency types
        
        for module in modules:
            # Add inheritance dependencies
            for cls in module.classes:
                for base_class in cls.base_classes:
                    # Find which module defines this base class
                    for other_module in self._module_map.values():
                        if other_module.name != module.name:
                            base_element = self._find_element_in_module(base_class, other_module)
                            if base_element and base_element.element_type == "class":
                                self.index.add_dependency(
                                    module.name, other_module.name,
                                    ReferenceType.INHERITANCE,
                                    f"{cls.name} inherits from {base_class}"
                                )
                                break
    
    async def _extract_event_flows(self, modules: List[Module]) -> None:
        """Extract event flow patterns from modules."""
        logger.debug("Extracting event flows...")
        
        event_types: Dict[str, EventFlow] = {}
        
        for module in modules:
            # Process module-level events
            for event in module.event_usage:
                self._add_event_to_flow(event, module.name, "", event_types)
            
            # Process class events
            for cls in module.classes:
                for event in cls.event_usage:
                    self._add_event_to_flow(event, module.name, cls.name, event_types)
                
                # Process method events
                for method in cls.methods:
                    for event in method.event_usage:
                        self._add_event_to_flow(event, module.name, f"{cls.name}.{method.name}", event_types)
            
            # Process function events
            for func in module.functions:
                for event in func.event_usage:
                    self._add_event_to_flow(event, module.name, func.name, event_types)
        
        self.index.event_flows = event_types
    
    def _add_event_to_flow(
        self, 
        event_usage, 
        module_name: str, 
        context: str,
        event_types: Dict[str, EventFlow]
    ) -> None:
        """Add an event usage to the flow tracking."""
        event_type = event_usage.event_type
        
        if event_type not in event_types:
            event_types[event_type] = EventFlow(
                event_type=event_type,
                pattern_name=event_usage.pattern_name
            )
        
        element_ref = ElementRef(
            name=context or module_name,
            module=module_name,
            element_type="function" if context and '.' not in context else "method" if '.' in context else "module",
            anchor=f"function-{context}" if context else f"module-{module_name}",
            file_path=Path(""),  # Will be filled in later
            location=event_usage.location
        )
        
        if event_usage.is_publisher:
            event_types[event_type].publishers.append(element_ref)
        
        if event_usage.is_subscriber:
            event_types[event_type].subscribers.append(element_ref)
    
    # Utility methods
    
    def _import_to_string(self, import_stmt: ImportStatement) -> str:
        """Convert import statement to string representation."""
        if import_stmt.module is None:
            names = ', '.join([alias or name for name, alias in import_stmt.names])
            return f"import {names}"
        else:
            names = ', '.join([f"{name} as {alias}" if alias else name for name, alias in import_stmt.names])
            return f"from {import_stmt.module} import {names}"
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the built index."""
        return {
            'total_modules': len(self.index.module_paths),
            'total_functions': len(self.index.functions),
            'total_classes': len(self.index.classes),
            'total_methods': len(self.index.methods),
            'resolved_imports': len(self.index.import_resolutions),
            'unresolved_imports': len(self.index.unresolved_imports),
            'type_resolutions': len(self.index.type_resolutions),
            'call_resolutions': len(self.index.call_resolutions),
            'dependencies': len(self.index.module_dependencies),
            'event_flows': len(self.index.event_flows)
        }


async def build_cross_reference_index(modules: List[Module]) -> CrossReferenceIndex:
    """
    Convenience function to build a cross-reference index from modules.
    
    Args:
        modules: List of parsed modules
        
    Returns:
        Complete cross-reference index
    """
    builder = IndexBuilder()
    return await builder.build_index(modules)