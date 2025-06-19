"""
Extraction verification tests.

Validates that extracted components work correctly with the new wbweb package structure.
This serves as both a test and documentation of the extraction process.
"""

import pytest


class TestHiccupRendererExtraction:
    """Verify HiccupRenderer extraction is successful."""
    
    def test_import_from_main_package(self):
        """Test importing HiccupRenderer from main wbweb package."""
        from wbweb import HiccupRenderer
        assert HiccupRenderer is not None
        
    def test_import_from_core_templates(self):
        """Test importing from wbweb.core.templates module."""
        from wbweb.core.templates import HiccupRenderer, HiccupTree
        assert HiccupRenderer is not None
        assert HiccupTree is not None
        
    def test_hiccup_tree_type_alias(self):
        """Test that HiccupTree type alias is properly exported."""
        from wbweb.core.templates import HiccupTree
        from typing import get_origin, get_args
        
        # Verify it's a Union type with str and List[Any]
        origin = get_origin(HiccupTree)
        assert origin is not None
        assert origin.__name__ in ['Union', 'UnionType']  # Handle different Python versions
        
    def test_basic_functionality(self):
        """Test basic HiccupRenderer functionality works after extraction."""
        from wbweb import HiccupRenderer
        
        renderer = HiccupRenderer()
        
        # Test simple text
        assert renderer.render("Hello") == "Hello"
        
        # Test simple tag
        result = renderer.render(["p", {}, "Hello wbweb!"])
        assert result == "<p>Hello wbweb!</p>"
        
        # Test tag with attributes
        result = renderer.render(["div", {"class": "extracted"}, "Success!"])
        assert result == '<div class="extracted">Success!</div>'
        
    def test_html_escaping_works(self):
        """Test HTML escaping functionality after extraction."""
        from wbweb.core.templates import HiccupRenderer
        
        renderer = HiccupRenderer()
        result = renderer.render(["p", {}, "<script>alert('test')</script>"])
        
        # Verify dangerous content is properly escaped
        assert "&lt;script&gt;" in result
        assert "alert(&#x27;test&#x27;)" in result
        assert "<script>" not in result
        
    def test_nested_structure_rendering(self):
        """Test complex nested structure rendering after extraction."""
        from wbweb import HiccupRenderer
        
        renderer = HiccupRenderer()
        complex_structure = [
            "div", {"class": "container", "id": "main"},
            ["h1", {}, "wbweb Extraction Test"],
            ["p", {"class": "description"}, "HiccupRenderer successfully extracted!"],
            ["ul", {},
                ["li", {}, "Import works"],
                ["li", {}, "Functionality preserved"],
                ["li", {}, "Tests passing"]
            ]
        ]
        
        result = renderer.render(complex_structure)
        
        # Verify structure is correctly rendered
        assert '<div class="container" id="main">' in result
        assert '<h1>wbweb Extraction Test</h1>' in result
        assert '<p class="description">HiccupRenderer successfully extracted!</p>' in result
        assert '<ul><li>Import works</li><li>Functionality preserved</li><li>Tests passing</li></ul>' in result
        

class TestPackageStructure:
    """Verify package structure is correctly set up."""
    
    def test_wbweb_main_module_structure(self):
        """Test main wbweb module has correct structure."""
        import wbweb
        
        # Check version is set
        assert hasattr(wbweb, '__version__')
        assert wbweb.__version__ == "0.1.0"
        
        # Check main exports are available
        assert hasattr(wbweb, 'HiccupRenderer')
        assert hasattr(wbweb, 'HiccupTree')
        
    def test_core_templates_module_structure(self):
        """Test core.templates module has correct structure."""
        from wbweb.core import templates
        
        # Check exports are available
        assert hasattr(templates, 'HiccupRenderer')
        assert hasattr(templates, 'HiccupTree')
        
        # Check __all__ is properly defined
        assert hasattr(templates, '__all__')
        assert 'HiccupRenderer' in templates.__all__
        assert 'HiccupTree' in templates.__all__
        
    def test_extraction_preserves_original_interface(self):
        """Test that extraction preserves the same interface as original."""
        from wbweb.core.templates import HiccupRenderer
        
        renderer = HiccupRenderer()
        
        # Check public methods exist
        assert hasattr(renderer, 'render')
        assert callable(renderer.render)
        
        # Check private methods exist (implementation details)
        assert hasattr(renderer, '_render_attributes')
        assert hasattr(renderer, '_escape_html')
        assert callable(renderer._render_attributes)
        assert callable(renderer._escape_html)