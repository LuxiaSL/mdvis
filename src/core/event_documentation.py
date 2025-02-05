"""
Event Documentation Module

This module aggregates event usage information from your parsed codebase
and generates a dedicated Markdown document for event flows. The document
lists each event type along with its publishers and subscribers and includes
a Mermaid diagram visualizing the event network.
"""

from collections import defaultdict
from typing import List, Dict, Set
from pathlib import Path

from src.models.code_elements import Module, EventUsage, Function, Class

def aggregate_event_usage(modules: List[Module]) -> Dict[str, Dict[str, Set[str]]]:
    """
    Aggregate event usage across all modules.
    
    Returns a dictionary keyed by event type, where each value is another dict:
        {
            "publishers": set of location strings,
            "subscribers": set of location strings
        }
    """
    events: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: {"publishers": set(), "subscribers": set()})
    
    def record_event(event: EventUsage, context: str, mode: str):
        # mode is either "publishers" or "subscribers"
        if event.event_type:
            events[event.event_type][mode].add(context)
    
    def traverse_function(func: Function, context_prefix: str = ""):
        # Build a context string for the function (including parent class if available)
        context = f"{context_prefix}.{func.name}" if context_prefix else func.name
        
        # Record events published and subscribed at the function level
        for ev in func.events_published:
            record_event(ev, context, "publishers")
        for ev in func.events_subscribed:
            record_event(ev, context, "subscribers")
            
        # Process nested functions recursively
        for nested in func.nested_functions:
            traverse_function(nested, context)
    
    def traverse_class(cls: Class, context_prefix: str = ""):
        # Build a context string for the class
        context = f"{context_prefix}.{cls.name}" if context_prefix else cls.name
        
        # Record events at the class level
        for ev in cls.events_published:
            record_event(ev, context, "publishers")
        for ev in cls.events_subscribed:
            record_event(ev, context, "subscribers")
        
        # Process methods in the class
        for method in cls.methods:
            traverse_function(method, context)
        # Optionally process inner classes if needed
        for inner in cls.inner_classes:
            traverse_class(inner, context)
    
    # Traverse each module
    for module in modules:
        # Use the module name as the context
        mod_context = module.name
        # Record module-level events (if any)
        for ev in module.events_published:
            record_event(ev, mod_context, "publishers")
        for ev in module.events_subscribed:
            record_event(ev, mod_context, "subscribers")
        
        # Process classes
        for cls in module.classes:
            traverse_class(cls, mod_context)
        
        # Process top-level functions
        for func in module.functions:
            traverse_function(func, mod_context)
    
    return events

def generate_event_mermaid_diagram(events: Dict[str, Dict[str, Set[str]]]) -> str:
    """
    Generate a Mermaid diagram (graph TD) representing event flows.
    Each event is a node; publishers and subscribers are connected by edges.
    """
    lines = ["```mermaid", "graph TD"]
    
    # Create nodes for each event type
    for event_type in events:
        # For clarity, prefix event types with "EV_"
        lines.append(f'    EV_{event_type.replace(" ", "_")}["{event_type}"]')
    
    # Draw edges: for each event, draw an edge from each publisher to the event,
    # then from the event to each subscriber.
    for event_type, data in events.items():
        event_node = f"EV_{event_type.replace(' ', '_')}"
        for pub in data["publishers"]:
            # Publisher nodes: we wrap them in quotes in case they have special characters
            pub_node = f'"{pub}"'
            lines.append(f"    {pub_node} --> {event_node}")
        for sub in data["subscribers"]:
            sub_node = f'"{sub}"'
            lines.append(f"    {event_node} --> {sub_node}")
    
    lines.append("```")
    return "\n".join(lines)

def generate_events_documentation(modules: List[Module], output_path: str) -> None:
    """
    Generate a Markdown document for events.
    The document includes:
      - A list of event types and their publishers/subscribers
      - A Mermaid diagram visualizing the event network.
    Write the document to the given output_path.
    """
    events = aggregate_event_usage(modules)
    md_lines = ["# Event System Documentation", ""]
    
    # Overview of events
    md_lines.append("## Event Types Overview")
    md_lines.append("")
    md_lines.append("Below is a list of all event types and their usage in the codebase:")
    md_lines.append("")
    
    for event_type, data in events.items():
        md_lines.append(f"### `{event_type}`")
        if data["publishers"]:
            md_lines.append("#### Publishers")
            for pub in sorted(data["publishers"]):
                md_lines.append(f"- [[{pub}]]")
        if data["subscribers"]:
            md_lines.append("#### Subscribers")
            for sub in sorted(data["subscribers"]):
                md_lines.append(f"- [[{sub}]]")
        md_lines.append("")  # blank line between events
    
    # Mermaid Diagram
    md_lines.append("## Event Flow Diagram")
    md_lines.append("")
    md_lines.append(generate_event_mermaid_diagram(events))
    md_lines.append("")
    
    # Write to disk
    output_file = Path(output_path)
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        print(f"Generated event documentation: {output_file}")
    except Exception as e:
        print(f"Error writing event documentation {output_file}: {e}")

# For testing or integration in your build chain, you might expose a main block:
if __name__ == "__main__":
    # Example usage:
    # Assume you have a list of modules already parsed by your system.
    from src.core.parser import parse_file
    import sys

    # This is a simple demo: parse a single file or list of files.
    # In practice, you'll integrate with your full codebase index.
    file_paths = sys.argv[1:]
    modules = []
    for fp in file_paths:
        try:
            mod = parse_file(fp)
            modules.append(mod)
        except Exception as e:
            print(f"Failed to parse {fp}: {e}")
    generate_events_documentation(modules, "Event_Documentation.md")
