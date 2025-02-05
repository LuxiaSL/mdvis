import os
import tempfile
from pathlib import Path
from src.core.scanner import scan_for_python_files, scan_for_python_files_generator

def test_scan_for_python_files():
    # Create a temporary directory with dummy Python files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create various test cases
        file_paths = [
            os.path.join(tmpdir, "file1.py"),
            os.path.join(tmpdir, "subdir", "file2.py"),
            os.path.join(tmpdir, "subdir", "nested", "file3.py"),
            os.path.join(tmpdir, "file_with_spaces.py"),
            os.path.join(tmpdir, ".hidden", "hidden.py")
        ]
        
        # Create directories
        for file_path in file_paths:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write("# dummy file\n")
                
        # Create some non-Python files
        with open(os.path.join(tmpdir, "not_python.txt"), "w") as f:
            f.write("not a python file")
        
        # Test regular function
        found_files = scan_for_python_files(tmpdir)
        assert len(found_files) == len(file_paths), "Should find all Python files"
        for fp in file_paths:
            assert any(str(Path(fp).resolve()) == found for found in found_files), f"Should find {fp}"
            
        # Test generator function
        found_files_gen = list(scan_for_python_files_generator(tmpdir))
        assert len(found_files_gen) == len(file_paths), "Generator should find all Python files"
        assert sorted(found_files) == sorted(found_files_gen), "Both functions should find same files"

def test_scan_empty_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        found_files = scan_for_python_files(tmpdir)
        assert len(found_files) == 0, "Should return empty list for directory with no Python files"
        
        found_files_gen = list(scan_for_python_files_generator(tmpdir))
        assert len(found_files_gen) == 0, "Generator should return no files for empty directory"

def test_scan_nonexistent_directory():
    nonexistent_dir = "/path/that/does/not/exist"
    try:
        scan_for_python_files(nonexistent_dir)
        assert False, "Should raise FileNotFoundError"
    except FileNotFoundError:
        pass
        
    try:
        list(scan_for_python_files_generator(nonexistent_dir))
        assert False, "Should raise FileNotFoundError"
    except FileNotFoundError:
        pass
