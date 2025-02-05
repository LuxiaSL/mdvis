from dataclasses import dataclass, field
from typing import List, Optional, Tuple

@dataclass
class ImportStatement:
    # For "import module" or "from module import ..." statements.
    module: Optional[str]  # For ImportFrom, module is provided; for Import it can be None.
    names: List[Tuple[str, Optional[str]]] = field(default_factory=list)  # (name, alias)

@dataclass
class Call:
    # Represents a function call chain, e.g. ["foo", "bar", "baz"] for foo.bar.baz(...).
    call_chain: List[str] = field(default_factory=list)

@dataclass
class Function:
    name: str
    parameters: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    calls: List[Call] = field(default_factory=list)
    nested_functions: List["Function"] = field(default_factory=list)
    is_async: bool = False  # Marks whether this function is asynchronous.
    line_number: int = 0    # Stores the line number of the function definition.
    parent_function: Optional["Function"] = None  # For nested functions.
    parent_class: Optional["Class"] = None         # New field for methods: the parent class.

@dataclass
class Class:
    name: str
    methods: List[Function] = field(default_factory=list)
    docstring: Optional[str] = None

@dataclass
class Module:
    name: str
    file_path: str
    classes: List[Class] = field(default_factory=list)
    functions: List[Function] = field(default_factory=list)
    imports: List[ImportStatement] = field(default_factory=list)
    source: Optional[str] = None  # Field to store the raw source code.
