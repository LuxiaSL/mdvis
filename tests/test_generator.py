import os
import sys
import tempfile
from pathlib import Path
from src.core.generator import generate_markdown, generate_dashboard, generate_anchor
from src.models.code_elements import Module, Class, Function, ImportStatement, Call

def test_generate_anchor():
    assert generate_anchor("Test Function") == "test-function"
    assert generate_anchor("test_function") == "test_function"
    assert generate_anchor("Test Function", "prefix") == "prefix-test-function"
    assert generate_anchor("", "prefix") == "prefix-"

def test_generate_markdown():
    # Create a temporary Python file with advanced constructs 
    python_content = '''
import os
from sys import version as sys_version
from typing import List, Optional

@decorator
class MyClass:
    """A sample class with comprehensive features."""
    
    class_var = 42
    
    @property
    def prop(self) -> int:
        """A property docstring."""
        return self.class_var
    
    def method_one(self, arg: str, opt: Optional[int] = None) -> None:
        """A sample method with type hints."""
        print(arg)
        def inner_func():
            """Inner function docstring."""
            return arg.upper()
        return inner_func()
        
    @staticmethod
    def static_method():
        """A static method."""
        return True
        
    async def async_method(self):
        """An async method."""
        await something()

def top_function(param: List[str]) -> None:
    """A top-level function with type hints."""
    os.path.join('a', 'b')
    module.submodule.function()
    obj.method().chain_call()

def empty_function():
    pass

class EmptyClass:
    pass
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(python_content)
        py_file = tmp.name

    with tempfile.TemporaryDirectory() as tmp_output:
        # Test basic markdown generation
        module_obj = generate_markdown(py_file, tmp_output)
        expected_md = Path(tmp_output) / (Path(py_file).stem + ".md")
        
        assert module_obj is not None, "Should return parsed Module object"
        assert expected_md.exists(), "Markdown file was not created"
        
        with open(expected_md, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # New tests for Obsidian-specific features
            assert "{#module-" in content, "Module anchor missing"
            assert "{#class-" in content, "Class anchor missing" 
            assert "{#method" in content, "Method anchor missing"
            assert "[[" in content and "]]" in content, "Obsidian links missing"
            
            # Test empty/minimal cases
            assert "empty_function" in content, "Empty function not documented"
            assert "EmptyClass" in content, "Empty class not documented"
            assert "**Parameters:** None" in content, "Empty parameters not handled"
            
            # Test nested structure formatting
            assert "#### Nested Functions" in content, "Nested functions header missing"
            assert "> " in content, "Docstring block quote missing"
            
            # Test call chain documentation
            assert "#### Calls" in content, "Function calls section missing"
            assert "obj.method().chain_call" in content, "Complex method chain not documented"

    os.remove(py_file)

def test_generate_markdown_with_unicode():
    python_content = '''
def unicode_func():
    """Function with üñîçødę characters."""
    pass
'''
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(python_content)
        py_file = tmp.name

    with tempfile.TemporaryDirectory() as tmp_output:
        generate_markdown(py_file, tmp_output)
        expected_md = Path(tmp_output) / (Path(py_file).stem + ".md")
        assert expected_md.exists()
        with open(expected_md, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "üñîçødę" in content

    os.remove(py_file)

def test_generate_dashboard_with_empty_modules():
    import tempfile
    from pathlib import Path
    from src.core.generator import generate_dashboard
    with tempfile.TemporaryDirectory() as tmp_output:
        generate_dashboard([], tmp_output)
        dashboard_file = Path(tmp_output) / "Dashboard.md"
        assert dashboard_file.exists()
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Should contain only the header when no modules exist.
            assert "# Codebase Dashboard" in content
            # Expect only one non-empty line (the header) in this case.
            non_empty_lines = [line for line in content.splitlines() if line.strip()]
            assert len(non_empty_lines) == 1

def test_generate_dashboard_file_permissions():
    # Skip this test on Windows since os.chmod behaves differently.
    if sys.platform.startswith("win"):
        import pytest
        pytest.skip("Skipping dashboard file permissions test on Windows")
        
    dummy_module = Module(name="test", file_path="test.py", source="")
    with tempfile.TemporaryDirectory() as tmp_output:
        # Make directory read-only
        os.chmod(tmp_output, 0o444)
        try:
            generate_dashboard([dummy_module], tmp_output)
            # Expect that the dashboard file was not created due to permission error.
            assert not (Path(tmp_output) / "Dashboard.md").exists()
        finally:
            # Reset permissions so cleanup can occur
            os.chmod(tmp_output, 0o777)

def test_generate_markdown_with_invalid_file():
    with tempfile.TemporaryDirectory() as tmp_output:
        # Test with non-existent file
        generate_markdown("nonexistent.py", tmp_output)
        assert len(list(Path(tmp_output).glob("*.md"))) == 0, "Should not create MD file for invalid input"

def test_generate_markdown_with_syntax_error():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        # Write invalid Python code
        tmp.write("this is not valid python code @@@@")
        py_file = tmp.name

    with tempfile.TemporaryDirectory() as tmp_output:
        generate_markdown(py_file, tmp_output)
        expected_md = Path(tmp_output) / (Path(py_file).stem + ".md")
        
        if expected_md.exists():
            with open(expected_md, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Warning" in content, "Should include warning for invalid Python code"

    os.remove(py_file)

def test_generate_dashboard():
    import tempfile
    from pathlib import Path
    from src.models.code_elements import Module
    from src.core.generator import generate_dashboard
    dummy_modules = [
        Module(name="moduleOne", file_path="dummy1.py", source="dummy source"),
        Module(name="moduleTwo", file_path="dummy2.py", source="dummy source"),
        Module(name="module with spaces", file_path="dummy3.py", source=""),
        Module(name="", file_path="empty.py", source=""),
        Module(name="module-with-dashes", file_path="dummy4.py", source="")
    ]

    with tempfile.TemporaryDirectory() as tmp_output:
        generate_dashboard(dummy_modules, tmp_output)
        dashboard_file = Path(tmp_output) / "Dashboard.md"
        assert dashboard_file.exists(), "Dashboard file was not created"

        with open(dashboard_file, "r", encoding="utf-8") as f:
            content = f.read()
            # Check header
            assert content.startswith("# Codebase Dashboard"), "Missing dashboard header"

            # Check that module links are present for modules with non-empty names.
            for module in dummy_modules:
                if module.name:
                    expected_link = f"[[{module.name}"
                    expected_anchor = f"#{{#module-{module.name.lower().replace(' ', '-')}}}"
                    assert expected_link in content, f"Missing module link for {module.name}"
                    assert expected_anchor in content, f"Missing anchor for {module.name}"

            # Now, verify that the section after the links is the dependency diagram heading.
            lines = content.splitlines()
            # Find the index of the "## Module Dependency Diagram" heading.
            diagram_heading_indices = [i for i, line in enumerate(lines) if line.strip() == "## Module Dependency Diagram"]
            assert diagram_heading_indices, "Dependency diagram heading missing"


def test_frontmatter_in_markdown():
    import tempfile
    from pathlib import Path
    from src.core.generator import generate_markdown
    python_content = '''
import os
from typing import List
from pathlib import Path

class TestClass:
    def method1(self): pass
    def method2(self): pass

class AnotherClass:
    pass

def function1(): pass
def function2(): pass
'''
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(python_content)
        py_file = tmp.name

    with tempfile.TemporaryDirectory() as tmp_output:
        module_obj = generate_markdown(py_file, tmp_output)
        md_file = Path(tmp_output) / (Path(py_file).stem + ".md")
        assert md_file.exists(), "Markdown file was not created"
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Now, because frontmatter is output at the very beginning, the file should start with ---
            assert content.startswith("---"), "YAML frontmatter not present at the top"
            # Check for expected frontmatter keys.
            assert "title:" in content, "Frontmatter missing title"
            assert "file_path:" in content, "Frontmatter missing file_path"
            assert "classes:" in content, "Frontmatter missing classes count"
            assert "functions:" in content, "Frontmatter missing functions count"
            assert "imports:" in content, "Frontmatter missing imports count"
            assert "tags:" in content, "Frontmatter missing tags"
    os.remove(py_file)

