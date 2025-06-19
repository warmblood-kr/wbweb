"""
Hiccup-style HTML renderer.

Converts Python data structures to HTML strings following Lisp hiccup conventions.
"""

from typing import Any, Dict, List, Union

HiccupTree = Union[str, List[Any]]


class HiccupRenderer:
    """Converts homoiconic data structures to HTML strings."""
    
    def render(self, hiccup_tree: HiccupTree) -> str:
        """Convert hiccup data structure to HTML string."""
        if isinstance(hiccup_tree, str):
            return self._escape_html(hiccup_tree)
        
        if isinstance(hiccup_tree, list) and len(hiccup_tree) >= 2:
            tag = hiccup_tree[0]
            attrs = hiccup_tree[1] if isinstance(hiccup_tree[1], dict) else {}
            children = hiccup_tree[2:] if isinstance(hiccup_tree[1], dict) else hiccup_tree[1:]
            
            attrs_str = self._render_attributes(attrs)
            children_str = ''.join(self.render(child) for child in children)
            return f'<{tag}{attrs_str}>{children_str}</{tag}>'
        
        return str(hiccup_tree)
    
    def _render_attributes(self, attrs: Dict[str, Any]) -> str:
        """Convert attribute dict to HTML attribute string."""
        if not attrs:
            return ''
        attr_pairs = [f'{k}="{self._escape_html(str(v))}"' for k, v in attrs.items()]
        return ' ' + ' '.join(attr_pairs)
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))