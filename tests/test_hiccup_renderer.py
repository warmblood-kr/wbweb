"""Test HiccupRenderer in isolation."""

import pytest
from wbweb.core.templates import HiccupRenderer


class TestHiccupRenderer:
    """Test the hiccup HTML renderer."""

    def test_render_simple_text(self):
        """Test rendering plain text."""
        renderer = HiccupRenderer()
        result = renderer.render("Hello")
        assert result == "Hello"

    def test_render_simple_tag(self):
        """Test rendering simple tag with text."""
        renderer = HiccupRenderer()
        result = renderer.render(["p", {}, "Hello"])
        assert result == "<p>Hello</p>"

    def test_render_tag_with_attributes(self):
        """Test rendering tag with attributes."""
        renderer = HiccupRenderer()
        result = renderer.render(["div", {"class": "message"}, "Hello"])
        assert result == '<div class="message">Hello</div>'

    def test_render_nested_tags(self):
        """Test rendering nested tags."""
        renderer = HiccupRenderer()
        result = renderer.render([
            "div", {"class": "container"},
            ["p", {}, "Hello"],
            ["span", {}, "World"]
        ])
        assert result == '<div class="container"><p>Hello</p><span>World</span></div>'

    def test_escape_html_special_chars(self):
        """Test HTML escaping."""
        renderer = HiccupRenderer()
        result = renderer.render(["p", {}, "<script>alert('xss')</script>"])
        assert result == "<p>&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;</p>"