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

    def test_raw_html_not_escaped(self):
        """Test that raw HTML content is not escaped."""
        from wbweb.core.templates.hiccup import raw
        renderer = HiccupRenderer()
        result = renderer.render(["div", {}, raw("<em>Hello</em> <strong>World</strong>")])
        assert result == "<div><em>Hello</em> <strong>World</strong></div>"

    def test_raw_html_mixed_with_escaped_content(self):
        """Test mixing raw HTML with regular escaped content."""
        from wbweb.core.templates.hiccup import raw
        renderer = HiccupRenderer()
        result = renderer.render([
            "div", {},
            "Safe text: <script>",
            raw("<em>Raw HTML</em>"),
            " & more safe text"
        ])
        assert result == "<div>Safe text: &lt;script&gt;<em>Raw HTML</em> &amp; more safe text</div>"

    def test_raw_html_in_attributes_still_escaped(self):
        """Test that raw HTML in attributes is still escaped for security."""
        from wbweb.core.templates.hiccup import raw
        renderer = HiccupRenderer()
        # Attributes should still be escaped even if we use raw for content
        result = renderer.render([
            "div", {"title": "<script>alert('xss')</script>"}, 
            raw("<em>Safe raw content</em>")
        ])
        assert result == '<div title="&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"><em>Safe raw content</em></div>'