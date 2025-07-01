# visualizations

> Visualization generation using Mermaid diagrams.

Creates various types of diagrams to visualize codebase structure,
dependencies, and relationships.

## Overview

- **Classes:** 1
- **Functions:** 1
- **Lines of Code:** 413

## Imports
- **from** `typing` **import** `List, Dict, Set, Optional, Tuple`
- **from** `pathlib` **import** `Path`
- **import** `logging`
- **from** `models.elements` **import** `Module, Class, Function`
- **from** `models.index` **import** `CrossReferenceIndex, DependencyEdge, ReferenceType`
- **from** `utils.text_processing` **import** `sanitize_anchor`

## Classes
### MermaidGenerator {#class-mermaidgenerator}

> Generates Mermaid diagrams for code visualization.


#### Methods
##### __init__ {#method-init}

> Initialize the Mermaid generator.

**Signature:** `def __init__(self, index: CrossReferenceIndex, max_nodes: int = 50)`
##### generate_dependency_graph {#method-generate-dependency-graph}

> Generate a module dependency graph.

**Signature:** `def generate_dependency_graph(self, modules: List[Module], exclude_external: bool = True, layout: str = 'LR') -> str`
##### generate_class_hierarchy {#method-generate-class-hierarchy}

> Generate a class inheritance hierarchy diagram.

**Signature:** `def generate_class_hierarchy(self, modules: List[Module], max_depth: int = 3) -> str`
##### generate_event_flow_diagram {#method-generate-event-flow-diagram}

> Generate an event flow diagram showing publishers and subscribers.

**Signature:** `def generate_event_flow_diagram(self, max_events: int = 20) -> str`
##### generate_function_call_graph {#method-generate-function-call-graph}

> Generate a function call graph showing call relationships.

**Signature:** `def generate_function_call_graph(self, modules: List[Module], focus_module: Optional[str] = None, max_functions: int = 30) -> str`
##### generate_module_overview {#method-generate-module-overview}

> Generate a high-level overview diagram of the codebase structure.

**Signature:** `def generate_module_overview(self, modules: List[Module]) -> str`
##### _sanitize_node_id {#method-sanitize-node-id}

> Sanitize a name for use as a Mermaid node ID.

**Signature:** `def _sanitize_node_id(self, name: str) -> str`

## Functions
### create_mermaid_generator {#function-create-mermaid-generator}

> Create a Mermaid diagram generator.

Args:
    index: Cross-reference index
    max_nodes: Maximum nodes per diagram
    
Returns:
    Configured Mermaid generator

**Signature:** `def create_mermaid_generator(index: CrossReferenceIndex, max_nodes: int = 50) -> MermaidGenerator`
