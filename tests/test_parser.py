from src.core.parser import parse_file

def test_parse_file_with_advanced_features(tmp_path):
    # Create a temporary Python file with various elements
    content = '''
import os
from sys import version, path as syspath
from typing import List, Optional as Opt

@decorator
class Sample:
    """Sample class docstring."""
    
    class_var = 123
    
    @property
    def prop(self) -> int:
        """Property docstring."""
        return 42
    
    @staticmethod
    def static_method():
        """Static method docstring."""
        return True
    
    async def async_method(self, value):
        """Async method docstring."""
        await something()
    
    def do_something(self, value: int, optional: Opt[str] = None) -> int:
        """Method docstring."""
        print(value)
        def nested_func(x: int) -> int:
            """Nested function docstring."""
            return x + 1
        return nested_func(value)
        
async def standalone(a: int, b: int) -> int:
    """A standalone function."""
    return a * b

def function_with_complex_calls():
    """Function with various call patterns."""
    os.path.join('a', 'b')
    module.submodule.function()
    obj.method().chained_call()
    '''
    file_path = tmp_path / "sample.py"
    file_path.write_text(content)

    module_obj = parse_file(str(file_path))
    
    # Test module properties
    assert module_obj.name == "sample"
    assert module_obj.file_path == str(file_path)

    # Test imports with aliases
    assert len(module_obj.imports) == 3
    assert module_obj.imports[0].module is None
    assert module_obj.imports[0].names[0][0] == "os"
    assert module_obj.imports[1].module == "sys"
    assert module_obj.imports[1].names[0][0] == "version"
    assert module_obj.imports[1].names[1][0] == "path"
    assert module_obj.imports[1].names[1][1] == "syspath"  # alias
    assert module_obj.imports[2].module == "typing"

    # Test class structure
    assert len(module_obj.classes) == 1
    sample_class = module_obj.classes[0]
    assert sample_class.name == "Sample"
    assert sample_class.docstring == "Sample class docstring."

    # Test method structure
    assert len(sample_class.methods) == 4
    method = sample_class.methods[2]  # async_method
    assert method.name == "async_method"
    assert method.docstring == "Async method docstring."
    assert method.parameters == ["self", "value"]
    assert method.is_async

    # Test property and static method
    assert any(m.name == "prop" for m in sample_class.methods)
    assert any(m.name == "static_method" for m in sample_class.methods)

    # Test method with type annotations
    do_something = next(m for m in sample_class.methods if m.name == "do_something")
    assert do_something.parameters == ["self", "value", "optional"]

    # Test nested function
    assert len(do_something.nested_functions) == 1
    nested = do_something.nested_functions[0]
    assert nested.name == "nested_func"
    assert nested.docstring == "Nested function docstring."
    assert nested.parameters == ["x"]

    # Test standalone functions
    assert len(module_obj.functions) == 2
    standalone = next(f for f in module_obj.functions if f.name == "standalone")
    assert standalone.name == "standalone"
    assert standalone.docstring == "A standalone function."
    assert standalone.parameters == ["a", "b"]
    assert standalone.is_async

    # Test function with complex calls
    complex_calls = next(f for f in module_obj.functions if f.name == "function_with_complex_calls")
    assert len(complex_calls.calls) >= 3
    assert any(call.call_chain == ["os", "path", "join"] for call in complex_calls.calls)
    assert any(call.call_chain == ["module", "submodule", "function"] for call in complex_calls.calls)

    # Test source code preservation
    assert "async def async_method" in module_obj.source
    assert "@property" in module_obj.source
    assert "@staticmethod" in module_obj.source
    assert "class Sample" in module_obj.source

    # Test line numbers and scope
    assert all(m.line_number > 0 for m in sample_class.methods)
    assert nested.parent_function == do_something
    assert do_something.parent_class == sample_class
