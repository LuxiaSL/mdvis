---
title: visualizations
type: module
file_path: /home/luxia/projects/mdvis/src/mdvis/output/visualizations.py
package: mdvis.output
stats:
  classes: 1
  functions: 1
  lines_of_code: 413
  complexity: 62
tags:
  - python
  - module
  - oop
---

# visualizations

> [!info] Documentation
> Visualization generation using Mermaid diagrams.
> 
> Creates various types of diagrams to visualize codebase structure,
> dependencies, and relationships.

## Table of Contents

### Classes
- [[#class-mermaidgenerator|MermaidGenerator]]

### Functions
- [[#function-create-mermaid-generator|create_mermaid_generator]]


## Imports

- **from** `typing` **import** `List`, `Dict`, `Set`, `Optional`, `Tuple`
- **from** `pathlib` **import** `Path`
- **import** `logging`
- **from** `models.elements` **import** [[elements#class-module|Module]], [[elements#class-class|Class]], [[elements#class-function|Function]]
- **from** `models.index` **import** [[index#class-crossreferenceindex|CrossReferenceIndex]], [[index#class-dependencyedge|DependencyEdge]], [[index#class-referencetype|ReferenceType]]
- **from** `utils.text_processing` **import** [[text_processing#function-sanitize-anchor|sanitize_anchor]]

## Classes

### MermaidGenerator {#class-mermaidgenerator}

> [!info] Documentation
> Generates Mermaid diagrams for code visualization.

#### Methods

##### generate_dependency_graph {#method-generate-dependency-graph}

**Signature:** `def generate_dependency_graph(self, modules: List[Module], exclude_external: bool = True, layout: str = 'LR') -> str`

> [!info] Documentation
> Generate a module dependency graph.
> 
> Args:
>     modules: List of modules to include
>     exclude_external: Whether to exclude external dependencies
>     layout: Mermaid layout direction (LR, TD, etc.)
>     
> Returns:
>     Mermaid diagram code

**Returns:** `str`


##### generate_class_hierarchy {#method-generate-class-hierarchy}

**Signature:** `def generate_class_hierarchy(self, modules: List[Module], max_depth: int = 3) -> str`

> [!info] Documentation
> Generate a class inheritance hierarchy diagram.
> 
> Args:
>     modules: List of modules containing classes
>     max_depth: Maximum inheritance depth to show
>     
> Returns:
>     Mermaid diagram code

**Returns:** `str`


##### generate_event_flow_diagram {#method-generate-event-flow-diagram}

**Signature:** `def generate_event_flow_diagram(self, max_events: int = 20) -> str`

> [!info] Documentation
> Generate an event flow diagram showing publishers and subscribers.
> 
> Args:
>     max_events: Maximum number of events to include
>     
> Returns:
>     Mermaid diagram code

**Returns:** `str`


##### generate_function_call_graph {#method-generate-function-call-graph}

**Signature:** `def generate_function_call_graph(self, modules: List[Module], focus_module: Optional[str] = None, max_functions: int = 30) -> str`

> [!info] Documentation
> Generate a function call graph showing call relationships.
> 
> Args:
>     modules: List of modules to analyze
>     focus_module: Optional module to focus on (shows calls to/from this module)
>     max_functions: Maximum number of functions to include
>     
> Returns:
>     Mermaid diagram code

**Returns:** `str`


##### generate_module_overview {#method-generate-module-overview}

**Signature:** `def generate_module_overview(self, modules: List[Module]) -> str`

> [!info] Documentation
> Generate a high-level overview diagram of the codebase structure.
> 
> Args:
>     modules: List of modules to visualize
>     
> Returns:
>     Mermaid diagram code

**Returns:** `str`



## Functions

### create_mermaid_generator {#function-create-mermaid-generator}

**Signature:** `def create_mermaid_generator(index: CrossReferenceIndex, max_nodes: int = 50) -> MermaidGenerator`

> [!info] Documentation
> Create a Mermaid diagram generator.
> 
> Args:
>     index: Cross-reference index
>     max_nodes: Maximum nodes per diagram
>     
> Returns:
>     Configured Mermaid generator

**Returns:** [[visualizations#class-mermaidgenerator|MermaidGenerator]]


## Source Code

```python
"""
Visualization generation using Mermaid diagrams.

Creates various types of diagrams to visualize codebase structure,
dependencies, and relationships.
"""

from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path
import logging

from ..models.elements import Module, Class, Function
from ..models.index import CrossReferenceIndex, DependencyEdge, ReferenceType
from ..utils.text_processing import sanitize_anchor

logger = logging.getLogger(__name__)


class MermaidGenerator:
    """
    Generates Mermaid diagrams for code visualization.
    """
    
    def __init__(self, index: CrossReferenceIndex, max_nodes: int = 50):
        """
        Initialize the Mermaid generator.
        
        Args:
            index: Cross-reference index with relationships
            max_nodes: Maximum nodes to include in diagrams
        """
        self.index = index
        self.max_nodes = max_nodes
    
    def generate_dependency_graph(
        self, 
        modules: List[Module],
        exclude_external: bool = True,
        layout: str = "LR"
    ) -> str:
        """
        Generate a module dependency graph.
        
        Args:
            modules: List of modules to include
            exclude_external: Whether to exclude external dependencies
            layout: Mermaid layout direction (LR, TD, etc.)
            
        Returns:
            Mermaid diagram code
        """
        lines = [f"```mermaid", f"graph {layout}"]
        
        # Get module names for filtering
        module_names = {module.name for module in modules}
        
        # Add nodes
        for module in modules[:self.max_nodes]:
            node_id = self._sanitize_node_id(module.name)
            node_label = module.name
            
            # Add styling based on module characteristics
            if module.classes:
                lines.append(f"    {node_id}[{node_label}]:::classModule")
            elif any(func.is_async for func in module.functions):
                lines.append(f"    {node_id}[{node_label}]:::asyncModule")
            else:
                lines.append(f"    {node_id}[{node_label}]")
        
        # Add dependencies
        for edge in self.index.module_dependencies:
            if exclude_external:
                if edge.target_module not in module_names:
                    continue
            
            source_id = self._sanitize_node_id(edge.source_module)
            target_id = self._sanitize_node_id(edge.target_module)
            
            # Different arrow styles for different dependency types
            if edge.dependency_type == ReferenceType.IMPORT:
                lines.append(f"    {source_id} --> {target_id}")
            elif edge.dependency_type == ReferenceType.INHERITANCE:
                lines.append(f"    {source_id} -.-> {target_id}")
            elif edge.dependency_type == ReferenceType.FUNCTION_CALL:
                lines.append(f"    {source_id} ---> {target_id}")
        
        # Add styling
        lines.extend([
            "    classDef classModule fill:#e1f5fe",
            "    classDef asyncModule fill:#f3e5f5",
            "```"
        ])
        
        return "\n".join(lines)
    
    def generate_class_hierarchy(
        self, 
        modules: List[Module],
        max_depth: int = 3
    ) -> str:
        """
        Generate a class inheritance hierarchy diagram.
        
        Args:
            modules: List of modules containing classes
            max_depth: Maximum inheritance depth to show
            
        Returns:
            Mermaid diagram code
        """
        lines = ["```mermaid", "graph TD"]
        
        # Collect all classes and their relationships
        classes = []
        inheritance_map = {}
        
        for module in modules:
            for cls in module.classes:
                classes.append((module.name, cls))
                if cls.base_classes:
                    inheritance_map[cls.name] = cls.base_classes
        
        # Limit to max_nodes classes
        classes = classes[:self.max_nodes]
        
        # Add class nodes
        for module_name, cls in classes:
            node_id = self._sanitize_node_id(f"{module_name}_{cls.name}")
            node_label = cls.name
            
            # Style based on class characteristics
            if cls.is_abstract:
                lines.append(f"    {node_id}[{node_label}]:::abstract")
            elif cls.is_dataclass:
                lines.append(f"    {node_id}[{node_label}]:::dataclass")
            elif cls.is_exception:
                lines.append(f"    {node_id}[{node_label}]:::exception")
            else:
                lines.append(f"    {node_id}[{node_label}]")
        
        # Add inheritance relationships
        for module_name, cls in classes:
            child_id = self._sanitize_node_id(f"{module_name}_{cls.name}")
            
            for base_class in cls.base_classes:
                # Try to find the base class in our modules
                base_id = None
                for other_module_name, other_cls in classes:
                    if other_cls.name == base_class:
                        base_id = self._sanitize_node_id(f"{other_module_name}_{other_cls.name}")
                        break
                
                if base_id:
                    lines.append(f"    {base_id} --> {child_id}")
                else:
                    # External base class
                    external_id = self._sanitize_node_id(base_class)
                    lines.append(f"    {external_id}[{base_class}]:::external")
                    lines.append(f"    {external_id} --> {child_id}")
        
        # Add styling
        lines.extend([
            "    classDef abstract fill:#ffebee,stroke:#d32f2f",
            "    classDef dataclass fill:#e8f5e8,stroke:#4caf50", 
            "    classDef exception fill:#fff3e0,stroke:#ff9800",
            "    classDef external fill:#f5f5f5,stroke:#9e9e9e,stroke-dasharray: 5 5",
            "```"
        ])
        
        return "\n".join(lines)
    
    def generate_event_flow_diagram(self, max_events: int = 20) -> str:
        """
        Generate an event flow diagram showing publishers and subscribers.
        
        Args:
            max_events: Maximum number of events to include
            
        Returns:
            Mermaid diagram code
        """
        if not self.index.event_flows:
            return "```mermaid\ngraph TD\n    NoEvents[No Events Detected]\n```"
        
        lines = ["```mermaid", "graph TD"]
        
        # Limit events to show
        events_to_show = list(self.index.event_flows.items())[:max_events]
        
        # Add event nodes
        for event_type, event_flow in events_to_show:
            event_id = self._sanitize_node_id(f"event_{event_type}")
            lines.append(f"    {event_id}[{event_type}]:::event")
        
        # Add publisher and subscriber nodes and connections
        for event_type, event_flow in events_to_show:
            event_id = self._sanitize_node_id(f"event_{event_type}")
            
            # Add publishers
            for publisher in event_flow.publishers[:5]:  # Limit to 5 publishers per event
                pub_id = self._sanitize_node_id(f"pub_{publisher.module}_{publisher.name}")
                pub_label = f"{publisher.module}.{publisher.name}" if publisher.name != publisher.module else publisher.name
                lines.append(f"    {pub_id}[{pub_label}]:::publisher")
                lines.append(f"    {pub_id} --> {event_id}")
            
            # Add subscribers
            for subscriber in event_flow.subscribers[:5]:  # Limit to 5 subscribers per event
                sub_id = self._sanitize_node_id(f"sub_{subscriber.module}_{subscriber.name}")
                sub_label = f"{subscriber.module}.{subscriber.name}" if subscriber.name != subscriber.module else subscriber.name
                lines.append(f"    {sub_id}[{sub_label}]:::subscriber")
                lines.append(f"    {event_id} --> {sub_id}")
        
        # Add styling
        lines.extend([
            "    classDef event fill:#fff9c4,stroke:#f57f17",
            "    classDef publisher fill:#e8f5e8,stroke:#4caf50",
            "    classDef subscriber fill:#e3f2fd,stroke:#2196f3",
            "```"
        ])
        
        return "\n".join(lines)
    
    def generate_function_call_graph(
        self, 
        modules: List[Module],
        focus_module: Optional[str] = None,
        max_functions: int = 30
    ) -> str:
        """
        Generate a function call graph showing call relationships.
        
        Args:
            modules: List of modules to analyze
            focus_module: Optional module to focus on (shows calls to/from this module)
            max_functions: Maximum number of functions to include
            
        Returns:
            Mermaid diagram code
        """
        lines = ["```mermaid", "graph LR"]
        
        # Collect functions and their calls
        functions = []
        call_relationships = []
        
        for module in modules:
            for func in module.get_all_functions():
                if focus_module and module.name != focus_module:
                    # Only include functions that call or are called by focus module
                    has_relationship = False
                    for call in func.calls:
                        call_resolution = self.index.resolve_call(call.call_chain, module.name)
                        if call_resolution and call_resolution.resolved_to:
                            if call_resolution.resolved_to.module == focus_module:
                                has_relationship = True
                                break
                    if not has_relationship:
                        continue
                
                functions.append((module.name, func))
                
                # Track call relationships
                for call in func.calls:
                    call_resolution = self.index.resolve_call(call.call_chain, module.name)
                    if call_resolution and call_resolution.resolved_to and not call_resolution.is_external:
                        call_relationships.append((
                            (module.name, func.name),
                            (call_resolution.resolved_to.module, call_resolution.resolved_to.name)
                        ))
        
        # Limit functions
        functions = functions[:max_functions]
        
        # Add function nodes
        for module_name, func in functions:
            node_id = self._sanitize_node_id(f"{module_name}_{func.name}")
            node_label = f"{func.name}"
            
            if func.is_async:
                lines.append(f"    {node_id}[{node_label}]:::async")
            elif func.parent_class:
                lines.append(f"    {node_id}[{node_label}]:::method")
            else:
                lines.append(f"    {node_id}[{node_label}]")
        
        # Add call relationships
        function_keys = {(m.name, f.name) for m, f in functions}
        
        for (caller_module, caller_name), (callee_module, callee_name) in call_relationships:
            if (caller_module, caller_name) in function_keys and (callee_module, callee_name) in function_keys:
                caller_id = self._sanitize_node_id(f"{caller_module}_{caller_name}")
                callee_id = self._sanitize_node_id(f"{callee_module}_{callee_name}")
                lines.append(f"    {caller_id} --> {callee_id}")
        
        # Add styling
        lines.extend([
            "    classDef async fill:#f3e5f5,stroke:#9c27b0",
            "    classDef method fill:#e1f5fe,stroke:#03a9f4",
            "```"
        ])
        
        return "\n".join(lines)
    
    def generate_module_overview(self, modules: List[Module]) -> str:
        """
        Generate a high-level overview diagram of the codebase structure.
        
        Args:
            modules: List of modules to visualize
            
        Returns:
            Mermaid diagram code
        """
        lines = ["```mermaid", "graph TD"]
        
        # Group modules by package
        packages = {}
        for module in modules:
            package = module.package or "root"
            if package not in packages:
                packages[package] = []
            packages[package].append(module)
        
        # Add package subgraphs
        for package_name, package_modules in packages.items():
            if package_name != "root":
                package_id = self._sanitize_node_id(package_name)
                lines.append(f"    subgraph {package_id} [{package_name}]")
                
                for module in package_modules[:10]:  # Limit modules per package
                    module_id = self._sanitize_node_id(module.name)
                    class_count = len(module.classes)
                    func_count = len(module.functions)
                    
                    if class_count > 0:
                        lines.append(f"        {module_id}[{module.name}<br/>Classes: {class_count}]:::withClasses")
                    elif func_count > 0:
                        lines.append(f"        {module_id}[{module.name}<br/>Functions: {func_count}]:::functionsOnly")
                    else:
                        lines.append(f"        {module_id}[{module.name}]")
                
                lines.append("    end")
            else:
                # Root level modules
                for module in package_modules[:10]:
                    module_id = self._sanitize_node_id(module.name)
                    class_count = len(module.classes)
                    func_count = len(module.functions)
                    
                    if class_count > 0:
                        lines.append(f"    {module_id}[{module.name}<br/>Classes: {class_count}]:::withClasses")
                    elif func_count > 0:
                        lines.append(f"    {module_id}[{module.name}<br/>Functions: {func_count}]:::functionsOnly")
                    else:
                        lines.append(f"    {module_id}[{module.name}]")
        
        # Add high-level dependencies between packages
        package_deps = set()
        for edge in self.index.module_dependencies:
            source_package = next((pkg for pkg, mods in packages.items() 
                                 if any(m.name == edge.source_module for m in mods)), "root")
            target_package = next((pkg for pkg, mods in packages.items() 
                                 if any(m.name == edge.target_module for m in mods)), "root")
            
            if source_package != target_package and source_package != "root" and target_package != "root":
                package_deps.add((source_package, target_package))
        
        for source_pkg, target_pkg in package_deps:
            source_id = self._sanitize_node_id(source_pkg)
            target_id = self._sanitize_node_id(target_pkg)
            lines.append(f"    {source_id} -.-> {target_id}")
        
        # Add styling
        lines.extend([
            "    classDef withClasses fill:#e8f5e8,stroke:#4caf50",
            "    classDef functionsOnly fill:#e3f2fd,stroke:#2196f3",
            "```"
        ])
        
        return "\n".join(lines)
    
    def _sanitize_node_id(self, name: str) -> str:
        """
        Sanitize a name for use as a Mermaid node ID.
        
        Args:
            name: Name to sanitize
            
        Returns:
            Sanitized node ID
        """
        # Replace problematic characters
        sanitized = name.replace(".", "_").replace("-", "_").replace(" ", "_")
        # Remove any remaining problematic characters
        sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = "n" + sanitized
        return sanitized or "node"


def create_mermaid_generator(index: CrossReferenceIndex, max_nodes: int = 50) -> MermaidGenerator:
    """
    Create a Mermaid diagram generator.
    
    Args:
        index: Cross-reference index
        max_nodes: Maximum nodes per diagram
        
    Returns:
        Configured Mermaid generator
    """
    return MermaidGenerator(index, max_nodes)
```