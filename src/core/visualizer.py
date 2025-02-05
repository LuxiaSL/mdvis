"""
Visualizer Module

This module generates Mermaid diagram syntax from
a list of parsed Module objects.
We generate a simple dependency graph (graph TD) where an
edge from Module A to Module B indicates that A imports B.
"""

import logging
from typing import List, Set
from ..models.code_elements import Module

def generate_global_dependency_diagram(modules: List[Module]) -> str:
    """
    Generate a Mermaid diagram showing dependencies between modules.
    Each node represents a module, and
    an edge from A to B indicates that A imports B.
    
    :param modules: List of Module objects.
    :return: A string containing Mermaid diagram syntax.
    """
    try:
        module_names: Set[str] = {module.name for module in modules if module.name}
        edges = set()

        for module in modules:
            if not module.name:
                continue
            for imp in module.imports:
                if imp.module and imp.module in module_names:
                    edge = f"{module.name} --> {imp.module}"
                    edges.add(edge)
                    
        diagram_lines = ["```mermaid", "graph TD"]
        diagram_lines.extend(sorted(edges))
        diagram_lines.append("```")
        return "\n".join(diagram_lines)
    except Exception as e:
        logging.exception("Error generating Mermaid diagram: %s", e)
        return ""
