from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Set

@dataclass
class ImportStatement:
    module: Optional[str]
    names: List[Tuple[str, Optional[str]]] = field(default_factory=list)
    is_internal: bool = False  # Track if import is from our codebase

@dataclass
class Call:
    call_chain: List[str] = field(default_factory=list)
    is_async: bool = False

@dataclass
class EventUsage:
    """Tracks how an event type is used in the code."""
    event_type: str
    publisher_locations: List[str] = field(default_factory=list)  # Where this event is dispatched
    subscriber_locations: List[str] = field(default_factory=list)  # Where this event is listened to
    is_async: bool = False
    priority: Optional[int] = None
    event_data_type: Optional[str] = None  # If we can determine the data type

@dataclass
class Attribute:
    """Class or instance attribute."""
    name: str
    type_hint: Optional[str] = None
    is_property: bool = False
    is_class_var: bool = False
    default_value: Optional[str] = None
    docstring: Optional[str] = None

@dataclass
class MethodMetrics:
    """Detailed metrics for a method."""
    complexity: int = 0  # Cyclomatic complexity
    lines_of_code: int = 0
    parameter_count: int = 0
    local_var_count: int = 0
    returns_count: int = 0
    branch_depth: int = 0  # Maximum nesting depth

@dataclass
class Function:
    name: str
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None  # Added return type annotation
    docstring: Optional[str] = None
    calls: List[Call] = field(default_factory=list)
    nested_functions: List["Function"] = field(default_factory=list)
    is_async: bool = False
    line_number: int = 0
    end_line: int = 0  # Added end line tracking
    parent_function: Optional["Function"] = None
    parent_class: Optional["Class"] = None
    decorators: List[str] = field(default_factory=list)
    metrics: MethodMetrics = field(default_factory=MethodMetrics)
    local_variables: List[str] = field(default_factory=list)
    raised_exceptions: List[str] = field(default_factory=list)
    caught_exceptions: List[str] = field(default_factory=list)
    events_published: List[EventUsage] = field(default_factory=list)
    events_subscribed: List[EventUsage] = field(default_factory=list)

@dataclass
class ClassMetrics:
    """Detailed metrics for a class."""
    total_methods: int = 0
    public_methods: int = 0
    private_methods: int = 0
    protected_methods: int = 0
    static_methods: int = 0
    class_methods: int = 0
    abstract_methods: int = 0
    property_count: int = 0
    total_lines: int = 0
    complexity: float = 0.0  # Average method complexity
    inheritance_depth: int = 0
    method_count_inherited: int = 0
    abstractness: float = 0.0  # Ratio of abstract methods
    weighted_method_count: int = 0  # Sum of method complexities

@dataclass
class Class:
    name: str
    methods: List[Function] = field(default_factory=list)
    docstring: Optional[str] = None
    base_classes: List[str] = field(default_factory=list)
    attributes: List[Attribute] = field(default_factory=list)
    metrics: ClassMetrics = field(default_factory=ClassMetrics)
    implemented_interfaces: List[str] = field(default_factory=list)
    inner_classes: List["Class"] = field(default_factory=list)
    events_published: List[EventUsage] = field(default_factory=list)
    events_subscribed: List[EventUsage] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)  # Other classes this one depends on

@dataclass
class ModuleMetrics:
    """Module-level metrics."""
    lines_of_code: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    class_count: int = 0
    function_count: int = 0
    import_count: int = 0
    avg_class_size: float = 0.0
    avg_function_size: float = 0.0
    complexity: float = 0.0
    dependency_count: int = 0

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
    metrics: ModuleMetrics = field(default_factory=ModuleMetrics)
    events_published: List[EventUsage] = field(default_factory=list)
    events_subscribed: List[EventUsage] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)  # Other modules this one depends on