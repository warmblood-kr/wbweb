"""
Hiccup-style HTML renderer.

Converts Python data structures to HTML strings following Lisp hiccup conventions.
"""

from typing import Any, Dict, List, Union

HiccupTree = Union[str, List[Any]]


class _RawHTML:
    """Internal wrapper for raw HTML content that should not be escaped.
    
    This class should not be instantiated directly. Use the raw() function instead.
    """
    
    def __init__(self, content: str):
        self.content = str(content)


def raw(content: str) -> _RawHTML:
    """Mark content as raw HTML that should not be escaped.
    
    Usage:
        ['div', {}, raw("<em>This will not be escaped</em>")]
    
    Args:
        content: HTML content that should be rendered without escaping
        
    Returns:
        A special object that the HiccupRenderer recognizes as raw content
    """
    return _RawHTML(content)


class HiccupRenderer:
    """Converts homoiconic data structures to HTML strings."""
    
    def render(self, hiccup_tree: HiccupTree) -> str:
        """Convert hiccup data structure to HTML string."""
        if isinstance(hiccup_tree, _RawHTML):
            return hiccup_tree.content
        
        if isinstance(hiccup_tree, str):
            return self._escape_html(hiccup_tree)
        
        if isinstance(hiccup_tree, list) and len(hiccup_tree) >= 2:
            tag = hiccup_tree[0]
            attrs = hiccup_tree[1] if isinstance(hiccup_tree[1], dict) else {}
            children = hiccup_tree[2:] if isinstance(hiccup_tree[1], dict) else hiccup_tree[1:]

            attrs_str = self._render_attributes(attrs)
            children_str = '\n'.join(self.render(child) for child in children)

            def is_unary_tag(tag):
                return tag in ['img', 'br', 'hr', 'embed', 'link', 'meta', 'source', 'track', 'wbr']

            if is_unary_tag(tag):
                return f'<{tag}{attrs_str}/>\n'
            else:
                return f'<{tag}{attrs_str}>{children_str}</{tag}>\n'
        
        return str(hiccup_tree)
    
    def _render_attributes(self, attrs: Dict[str, Any]) -> str:
        """Convert attribute dict to HTML attribute string."""
        if not attrs:
            return ''

        def is_unary_attr(k):
            return k in ['checked', 'disabled', 'multiple', 'readonly', 'required']

        def render_attr(k, v):
            if is_unary_attr(k) and v is True:
                return str(k)

            return f'{k}="{self._escape_html(str(v))}"'

        attr_pairs = [
            render_attr(k, v)
            for k, v in attrs.items()
        ]

        return ' ' + ' '.join(attr_pairs)
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))
