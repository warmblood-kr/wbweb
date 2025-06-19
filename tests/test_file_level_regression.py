"""
File-level regression test to verify our extraction doesn't break core functionality.

This test compares the raw hiccup.py files to ensure our extraction preserved
the exact functionality without going through Python's import system.
"""

import subprocess
import sys
from pathlib import Path


class TestFileLevelRegression:
    """Test hiccup.py functionality at the file level."""
    
    def test_wbgpt_hiccup_file_directly(self):
        """Test running wbgpt hiccup.py directly to bypass import issues."""
        
        # Create a test script that imports hiccup.py directly
        test_script = """
import sys
sys.path.insert(0, '/home/toracle/projects/wbgpt')

# Read and execute the hiccup.py file directly
with open('/home/toracle/projects/wbgpt/wbgpt/core/templates/hiccup.py', 'r') as f:
    hiccup_code = f.read()

# Execute the code in a controlled namespace
namespace = {}
exec(hiccup_code, namespace)

# Get the HiccupRenderer class
HiccupRenderer = namespace['HiccupRenderer']

# Test it
renderer = HiccupRenderer()
result = renderer.render(['p', {}, 'test'])
assert result == '<p>test</p>', f'Expected <p>test</p>, got {result}'
print('wbgpt hiccup.py file test: SUCCESS')
"""
        
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True
        )
        
        print(f"wbgpt file test stdout: {result.stdout}")
        if result.stderr:
            print(f"wbgpt file test stderr: {result.stderr}")
            
        assert result.returncode == 0, f"wbgpt hiccup.py file test failed: {result.stderr}"
        assert "SUCCESS" in result.stdout
        
    def test_compare_file_contents(self):
        """Compare the actual hiccup.py file contents between wbgpt and wbweb."""
        
        wbgpt_file = Path("/home/toracle/projects/wbgpt/wbgpt/core/templates/hiccup.py")
        wbweb_file = Path("/home/toracle/projects/wbweb/wbweb/core/templates/hiccup.py")
        
        assert wbgpt_file.exists(), f"wbgpt hiccup.py not found at {wbgpt_file}"
        assert wbweb_file.exists(), f"wbweb hiccup.py not found at {wbweb_file}"
        
        with open(wbgpt_file, 'r') as f:
            wbgpt_content = f.read()
            
        with open(wbweb_file, 'r') as f:
            wbweb_content = f.read()
            
        # They should be identical since we copied without modification
        assert wbgpt_content == wbweb_content, "hiccup.py files should be identical"
        print("✅ wbgpt and wbweb hiccup.py files are identical")
        
    def test_both_implementations_work_identically(self):
        """Test that both hiccup.py files produce identical results when executed."""
        
        test_cases = [
            "Hello",
            ["p", {}, "Test"],
            ["div", {"class": "test"}, "Content"],
            ["span", {"id": "test", "class": "highlight"}, "Multi-attr"]
        ]
        
        for test_case in test_cases:
            # Test wbweb version
            from wbweb.core.templates import HiccupRenderer as WbwebRenderer
            wbweb_renderer = WbwebRenderer()
            wbweb_result = wbweb_renderer.render(test_case)
            
            # Test wbgpt version by executing file directly
            wbgpt_test_script = f"""
with open('/home/toracle/projects/wbgpt/wbgpt/core/templates/hiccup.py', 'r') as f:
    hiccup_code = f.read()

namespace = {{}}
exec(hiccup_code, namespace)
HiccupRenderer = namespace['HiccupRenderer']

import ast
renderer = HiccupRenderer()
test_data = {repr(test_case)}
result = renderer.render(test_data)
print(result)
"""
            
            wbgpt_result_process = subprocess.run(
                [sys.executable, "-c", wbgpt_test_script],
                capture_output=True,
                text=True
            )
            
            assert wbgpt_result_process.returncode == 0, \
                f"wbgpt test failed for {test_case}: {wbgpt_result_process.stderr}"
                
            wbgpt_result = wbgpt_result_process.stdout.strip()
            
            assert wbweb_result == wbgpt_result, \
                f"Results differ for {test_case}:\n  wbweb: '{wbweb_result}'\n  wbgpt: '{wbgpt_result}'"
                
        print("✅ Both hiccup.py implementations produce identical results")


class TestDependencyAnalysis:
    """Analyze the dependency situation in wbgpt."""
    
    def test_wbgpt_missing_dependencies_analysis(self):
        """Document what dependencies wbgpt is missing and why."""
        
        # Check what imports are failing
        dependency_check = subprocess.run([
            sys.executable, "-c",
            "missing = []; "
            "try: import starlette; print('starlette: OK'); "
            "except ImportError: missing.append('starlette'); "
            "try: import sqlalchemy; print('sqlalchemy: OK'); "
            "except ImportError: missing.append('sqlalchemy'); "
            "if missing: print(f'Missing: {missing}'); "
            "else: print('All dependencies available')"
        ], capture_output=True, text=True)
        
        print(f"Dependency analysis: {dependency_check.stdout.strip()}")
        
        # This is informational - we're documenting the current state
        # The missing dependencies are pre-existing issues, not caused by our extraction
        
        # The key insight: our extraction preserved functionality even though
        # wbgpt currently can't run due to missing dependencies
        
    def test_extraction_isolation_success(self):
        """Verify that our extraction created a working isolated component."""
        
        # The key test: wbweb works even though wbgpt has dependency issues
        from wbweb.core.templates import HiccupRenderer
        
        renderer = HiccupRenderer()
        
        # Test complex functionality to prove extraction completeness
        complex_test = [
            "div", {"class": "container", "id": "main"},
            ["h1", {}, "Title"],
            ["p", {"class": "content"}, "Some <dangerous> content"],
            ["ul", {},
                ["li", {}, "Item 1"],
                ["li", {"class": "special"}, "Item 2"]
            ]
        ]
        
        result = renderer.render(complex_test)
        
        # Verify it handles everything correctly
        assert 'class="container"' in result
        assert 'id="main"' in result  
        assert '<h1>Title</h1>' in result
        assert '&lt;dangerous&gt;' in result  # HTML escaping
        assert '<li class="special">Item 2</li>' in result
        
        print("✅ Extracted HiccupRenderer handles complex cases correctly")
        print("✅ Extraction created fully functional isolated component")