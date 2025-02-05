import os
import tempfile
from src.core.linter import run_linter, lint_file

def test_run_linter_success():
    tmp_path = None
    try:
        # Create a temporary file with valid Python code
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write("print('Hello World')\n")
            tmp_path = tmp.name

        # Test with flake8
        code, output = run_linter("flake8", tmp_path)
        assert code == 0, f"Expected code 0, got {code}. Output: {output}"

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_run_linter_with_errors():
    tmp_path = None
    try:
        # Create code with deliberate style errors
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write("def  bad_spacing():\n  x=1\n")
            tmp_path = tmp.name

        code, output = run_linter("flake8", tmp_path)
        assert code != 0, "Should detect style errors"
        assert output.strip(), "Should provide error output"

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_run_linter_invalid_command():
    code, output = run_linter("nonexistent_linter", "test.py")
    assert code == -1, "Should return error code for invalid linter"
    assert "error" in output.lower(), "Should include error message"

def test_lint_file():
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write("print('Test')\n")
            tmp_path = tmp.name
        
        # Test with multiple linters
        linters = {
            "flake8": "flake8",
            "nonexistent": "nonexistent_linter"
        }
        results = lint_file(tmp_path, linters)
        
        # Check flake8 results
        assert "flake8" in results
        code, output = results["flake8"]
        assert code == 0, f"Valid code should pass flake8: {output}"
        
        # Check nonexistent linter results
        assert "nonexistent" in results
        code, output = results["nonexistent"]
        assert code == -1, "Invalid linter should return error code"

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_lint_file_nonexistent_file():
    linters = {"flake8": "flake8"}
    results = lint_file("nonexistent_file.py", linters)
    code, output = results["flake8"]
    assert code != 0, "Should fail for nonexistent file"
