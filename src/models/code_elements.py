from dataclasses import dataclass, field
from typing import List, Optional, Tuple

@dataclass
class ImportStatement:
    module: Optional[str]
    names: List[Tuple[str, Optional[str]]] = field(default_factory=list)
    # e.g. for "from foo import bar as baz" => module="foo", names=[("bar", "baz")]

@dataclass
class Call:
    call_chain: List[str] = field(default_factory=list)

@dataclass
class Function:
    name: str
    parameters: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    calls: List[Call] = field(default_factory=list)
    nested_functions: List["Function"] = field(default_factory=list)
    is_async: bool = False
    line_number: int = 0
    parent_function: Optional["Function"] = None
    parent_class: Optional["Class"] = None
    decorators: List[str] = field(default_factory=list)  # e.g. ["@staticmethod"]

@dataclass
class Class:
    name: str
    methods: List[Function] = field(default_factory=list)
    docstring: Optional[str] = None
    base_classes: List[str] = field(default_factory=list)

@dataclass
class Module:
    name: str
    file_path: str
    classes: List[Class] = field(default_factory=list)
    functions: List[Function] = field(default_factory=list)
    imports: List[ImportStatement] = field(default_factory=list)
    source: Optional[str] = None
    todos: List[str] = field(default_factory=list)
    lint_warnings: List[str] = field(default_factory=list)
