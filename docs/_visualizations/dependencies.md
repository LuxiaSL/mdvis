# Module Dependencies

This diagram shows the dependencies between modules in the codebase.

```mermaid
graph LR
    n__init__[__init__]
    n__init__[__init__]
    async_patterns[async_patterns]
    events[events]
    metrics[metrics]
    types[types]
    cli[cli]:::classModule
    n__init__[__init__]
    manager[manager]:::classModule
    schema[schema]:::classModule
    n__init__[__init__]
    indexer[indexer]:::classModule
    parser[parser]:::classModule
    processor[processor]:::classModule
    scanner[scanner]:::classModule
    n__init__[__init__]
    elements[elements]:::classModule
    index[index]:::classModule
    n__init__[__init__]
    obsidian[obsidian]:::classModule
    templates[templates]:::classModule
    visualizations[visualizations]:::classModule
    n__init__[__init__]
    async_helpers[async_helpers]:::classModule
    text_processing[text_processing]
    classDef classModule fill:#e1f5fe
    classDef asyncModule fill:#f3e5f5
```

## Legend

- **Solid arrows** → Import dependencies
- **Dotted arrows** → Inheritance relationships  
- **Bold arrows** → Function call dependencies

Generated on: 2025-06-30 20:58:04
