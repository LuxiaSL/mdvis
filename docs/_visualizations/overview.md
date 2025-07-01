# Codebase Overview

High-level overview of the codebase structure and organization.

```mermaid
graph TD
    subgraph mdvis [mdvis]
        n__init__[__init__]
        cli[cli<br/>Classes: 1]:::withClasses
    end
    subgraph mdvis_analysis [mdvis.analysis]
        n__init__[__init__]
        async_patterns[async_patterns]
        events[events]
        metrics[metrics]
        types[types]
    end
    subgraph mdvis_config [mdvis.config]
        n__init__[__init__]
        manager[manager<br/>Classes: 2]:::withClasses
        schema[schema<br/>Classes: 8]:::withClasses
    end
    subgraph mdvis_core [mdvis.core]
        n__init__[__init__]
        indexer[indexer<br/>Classes: 1]:::withClasses
        parser[parser<br/>Classes: 1]:::withClasses
        processor[processor<br/>Classes: 2]:::withClasses
        scanner[scanner<br/>Classes: 2]:::withClasses
    end
    subgraph mdvis_models [mdvis.models]
        n__init__[__init__]
        elements[elements<br/>Classes: 14]:::withClasses
        index[index<br/>Classes: 8]:::withClasses
    end
    subgraph mdvis_output [mdvis.output]
        n__init__[__init__]
        obsidian[obsidian<br/>Classes: 1]:::withClasses
        templates[templates<br/>Classes: 2]:::withClasses
        visualizations[visualizations<br/>Classes: 1]:::withClasses
    end
    subgraph mdvis_utils [mdvis.utils]
        n__init__[__init__]
        async_helpers[async_helpers<br/>Classes: 1]:::withClasses
        text_processing[text_processing<br/>Functions: 14]:::functionsOnly
    end
    classDef withClasses fill:#e8f5e8,stroke:#4caf50
    classDef functionsOnly fill:#e3f2fd,stroke:#2196f3
```

## Statistics

- **Total modules:** 25
- **Total classes:** 44
- **Total functions:** 201
- **Total lines:** 6,623

Generated on: 2025-06-30 20:58:04
