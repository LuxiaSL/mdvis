# parser

> Enhanced AST parser for extracting rich code structure and metadata.

Parses Python source code to extract detailed information about classes, functions,
type hints, async patterns, and other code elements.

## Overview

- **Classes:** 1
- **Functions:** 0
- **Lines of Code:** 843

## Imports
- **import** `ast`
- **import** `re`
- **import** `asyncio`
- **import** `aiofiles`
- **from** `pathlib` **import** `Path`
- **from** `typing` **import** `Any, Dict, List, Optional, Set, Tuple, Union`
- **import** `logging`
- **from** `models.elements` **import** `Module, Class, Function, Parameter, TypeRef, Location, Decorator, ImportStatement, CallRef, EventUsage, AsyncPattern, AsyncPatternType, VisibilityLevel, Attribute`

## Classes
### EnhancedASTParser {#class-enhancedastparser}

> Enhanced AST parser that extracts detailed code structure and metadata.


#### Methods
##### __init__ {#method-init}

> Initialize the parser.

**Signature:** `def __init__(self, event_patterns: Optional[List[dict]] = None)`
##### _compile_event_patterns {#method-compile-event-patterns}

> Compile regex patterns for event detection..

**Signature:** `def _compile_event_patterns(self) -> List[dict]`
##### parse_file {#method-parse-file}

> Parse a Python file and return a Module object with rich metadata.

**Signature:** `async def parse_file(self, file_path: Path, source_code: Optional[str] = None) -> Module`
##### _determine_package {#method-determine-package}

> Determine the package name for a file based on its path..

**Signature:** `def _determine_package(self, file_path: Path) -> Optional[str]`
##### _parse_module_body {#method-parse-module-body}

> Parse the body of a module..

**Signature:** `def _parse_module_body(self, tree: ast.AST, module: Module, source_code: str) -> None`
##### _parse_class {#method-parse-class}

> Parse a class definition..

**Signature:** `def _parse_class(self, node: ast.ClassDef, source_code: str, parent_name: str = '') -> Class`
##### _parse_function {#method-parse-function}

> Parse a function or method definition..

**Signature:** `def _parse_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], source_code: str, parent_class: Optional[Class] = None, parent_function: Optional[Function] = None) -> Function`
##### _parse_parameters {#method-parse-parameters}

> Parse function parameters..

**Signature:** `def _parse_parameters(self, args: ast.arguments) -> List[Parameter]`
##### _parse_type_annotation {#method-parse-type-annotation}

> Parse a type annotation AST node..

**Signature:** `def _parse_type_annotation(self, annotation: ast.AST) -> Optional[TypeRef]`
##### _parse_generic_args {#method-parse-generic-args}

> Parse generic type arguments..

**Signature:** `def _parse_generic_args(self, slice_node: ast.AST) -> List[TypeRef]`
##### _parse_return_type {#method-parse-return-type}

> Parse function return type annotation..

**Signature:** `def _parse_return_type(self, node: ast.FunctionDef) -> Optional[TypeRef]`
##### _parse_import {#method-parse-import}

> Parse an import statement..

**Signature:** `def _parse_import(self, node: Union[ast.Import, ast.ImportFrom]) -> ImportStatement`
##### _parse_decorators {#method-parse-decorators}

> Parse decorators..

**Signature:** `def _parse_decorators(self, decorator_list: List[ast.AST]) -> List[Decorator]`
##### _parse_attribute {#method-parse-attribute}

> Parse an attribute assignment..

**Signature:** `def _parse_attribute(self, name: str, node: ast.Assign, source_code: str, is_class_var: bool = False) -> Optional[Attribute]`
##### _extract_function_calls {#method-extract-function-calls}

> Extract function calls from a function body..

**Signature:** `def _extract_function_calls(self, node: ast.FunctionDef) -> List[CallRef]`
##### _extract_call_chain {#method-extract-call-chain}

> Extract call chain from an AST node (e.g., obj.method.call -> ['obj', 'method', 'call'])..

**Signature:** `def _extract_call_chain(self, node: ast.AST) -> List[str]`
##### _extract_nested_functions {#method-extract-nested-functions}

> Extract nested functions from a function body..

**Signature:** `def _extract_nested_functions(self, node: ast.FunctionDef, source_code: str, parent_function: Function) -> List[Function]`
##### _generate_signature {#method-generate-signature}

> Generate a function signature string..

**Signature:** `def _generate_signature(self, node: ast.FunctionDef, parameters: List[Parameter]) -> str`
##### _determine_visibility {#method-determine-visibility}

> Determine visibility level based on naming convention..

**Signature:** `def _determine_visibility(self, name: str) -> VisibilityLevel`
##### _decorator_name {#method-decorator-name}

> Extract decorator name from AST node..

**Signature:** `def _decorator_name(self, decorator: ast.AST) -> str`
##### _ast_to_string {#method-ast-to-string}

> Convert AST node to string representation..

**Signature:** `def _ast_to_string(self, node: ast.AST) -> str`
##### _has_yield {#method-has-yield}

> Check if function contains yield statements..

**Signature:** `def _has_yield(self, node: ast.FunctionDef) -> bool`
##### _calculate_complexity {#method-calculate-complexity}

> Calculate cyclomatic complexity of a function..

**Signature:** `def _calculate_complexity(self, node: ast.FunctionDef) -> int`
##### _extract_base_classes {#method-extract-base-classes}

> Extract base class names..

**Signature:** `def _extract_base_classes(self, node: ast.ClassDef) -> List[str]`
##### _extract_type_references_from_node {#method-extract-type-references-from-node}

> Extract all type references from an AST node..

**Signature:** `def _extract_type_references_from_node(self, node: ast.AST) -> List[TypeRef]`
##### _extract_async_patterns_from_node {#method-extract-async-patterns-from-node}

> Extract async patterns from an AST node..

**Signature:** `def _extract_async_patterns_from_node(self, node: ast.AST) -> List[AsyncPattern]`
##### _extract_event_usage_from_node {#method-extract-event-usage-from-node}

> Extract event usage patterns from an AST node..

**Signature:** `def _extract_event_usage_from_node(self, node: ast.AST, source_code: str) -> List[EventUsage]`
##### _extract_event_type_from_call {#method-extract-event-type-from-call}

> Extract event type from a function call using the pattern's regex..

**Signature:** `def _extract_event_type_from_call(self, call_node: ast.Call, pattern_config: dict) -> Optional[str]`
##### _count_comment_lines {#method-count-comment-lines}

> Count lines that are primarily comments..

**Signature:** `def _count_comment_lines(self, source_code: str) -> int`
##### _extract_todos {#method-extract-todos}

> Extract TODO/FIXME comments from source code..

**Signature:** `def _extract_todos(self, source_code: str) -> List[str]`

