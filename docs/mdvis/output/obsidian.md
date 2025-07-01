# obsidian

> Obsidian markdown generator with smart cross-references.

Generates clean, navigable markdown documentation optimized for Obsidian
with proper wikilinks, anchors, and cross-references using templates and visualizations.

## Overview

- **Classes:** 1
- **Functions:** 0
- **Lines of Code:** 809

## Imports
- **import** `asyncio`
- **import** `aiofiles`
- **from** `pathlib` **import** `Path`
- **from** `typing` **import** `List, Dict, Any, Optional, Set`
- **from** `datetime` **import** `datetime`
- **import** `logging`
- **from** `config.schema` **import** `MDVisConfig`
- **from** `models.elements` **import** `Module, Class, Function, Parameter, ImportStatement, VisibilityLevel`
- **from** `models.index` **import** `CrossReferenceIndex`
- **from** `templates` **import** `create_template_manager`
- **from** `visualizations` **import** `create_mermaid_generator`

## Classes
### ObsidianGenerator {#class-obsidiangenerator}

> Generates Obsidian-compatible markdown documentation with smart linking.


#### Methods
##### __init__ {#method-init}

> Initialize the generator.

**Signature:** `def __init__(self, config: MDVisConfig, index: CrossReferenceIndex, project_root: Path = None)`
##### generate_documentation {#method-generate-documentation}

> Generate complete documentation for all modules.

**Signature:** `async def generate_documentation(self, modules: List[Module], output_root: Path) -> None`
##### _setup_output_structure {#method-setup-output-structure}

> Setup the output directory structure..

**Signature:** `async def _setup_output_structure(self, output_root: Path) -> None`
##### _generate_module_documentation {#method-generate-module-documentation}

> Generate documentation for a single module..

**Signature:** `async def _generate_module_documentation(self, module: Module, output_root: Path) -> None`
##### _generate_frontmatter {#method-generate-frontmatter}

> Generate YAML frontmatter for the module..

**Signature:** `def _generate_frontmatter(self, module: Module) -> List[str]`
##### _generate_module_content {#method-generate-module-content}

> Generate the markdown content for a module using templates..

**Signature:** `async def _generate_module_content(self, module: Module) -> str`
##### _generate_module_content_fallback {#method-generate-module-content-fallback}

> Fallback module content generation without templates..

**Signature:** `async def _generate_module_content_fallback(self, module: Module) -> str`
##### _generate_table_of_contents {#method-generate-table-of-contents}

> Generate table of contents for the module..

**Signature:** `def _generate_table_of_contents(self, module: Module) -> List[str]`
##### _generate_imports_section {#method-generate-imports-section}

> Generate the imports section..

**Signature:** `def _generate_imports_section(self, module: Module) -> List[str]`
##### _format_import_statement {#method-format-import-statement}

> Format an import statement with smart linking..

**Signature:** `def _format_import_statement(self, import_stmt: ImportStatement, module: Module) -> str`
##### _generate_class_section {#method-generate-class-section}

> Generate documentation for a class..

**Signature:** `def _generate_class_section(self, cls: Class, module: Module) -> List[str]`
##### _generate_function_section {#method-generate-function-section}

> Generate documentation for a function or method..

**Signature:** `def _generate_function_section(self, func: Function, module: Module, is_method: bool = False) -> List[str]`
##### _generate_parameters_section {#method-generate-parameters-section}

> Generate detailed parameters section..

**Signature:** `def _generate_parameters_section(self, parameters: List[Parameter], module: Module) -> List[str]`
##### _format_attribute {#method-format-attribute}

> Format an attribute for display..

**Signature:** `def _format_attribute(self, attr) -> str`
##### _format_type_reference {#method-format-type-reference}

> Format a type reference with smart linking..

**Signature:** `def _format_type_reference(self, type_ref, module: Module) -> str`
##### _format_call_reference {#method-format-call-reference}

> Format a function call reference with smart linking..

**Signature:** `def _format_call_reference(self, call, module: Module) -> str`
##### _format_docstring {#method-format-docstring}

> Format a docstring for display..

**Signature:** `def _format_docstring(self, docstring: str) -> List[str]`
##### _generate_source_section {#method-generate-source-section}

> Generate the source code section..

**Signature:** `def _generate_source_section(self, module: Module) -> List[str]`
##### _generate_todos_section {#method-generate-todos-section}

> Generate the TODOs section..

**Signature:** `def _generate_todos_section(self, todos: List[str]) -> List[str]`
##### _generate_dashboard {#method-generate-dashboard}

> Generate the main dashboard/index file..

**Signature:** `async def _generate_dashboard(self, modules: List[Module], output_root: Path) -> None`
##### _generate_dependency_visualization {#method-generate-dependency-visualization}

> Generate dependency visualization using Mermaid diagrams..

**Signature:** `async def _generate_dependency_visualization(self, modules: List[Module], output_root: Path) -> None`
##### _generate_event_documentation {#method-generate-event-documentation}

> Generate event flow documentation with visualizations..

**Signature:** `async def _generate_event_documentation(self, output_root: Path) -> None`
##### _should_include_element {#method-should-include-element}

> Check if an element should be included based on visibility settings..

**Signature:** `def _should_include_element(self, name: str) -> bool`

