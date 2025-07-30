"""
Renderer strategy classes for different client types.

Provides format-specific rendering following DRF-style renderer pattern.
"""

from typing import Any, Dict, List, Union
from starlette.requests import Request
from .hiccup import HiccupRenderer, HiccupTree


def get_preferred_format(request: Request) -> str:
    """Determine preferred response format from Accept header."""
    accept = request.headers.get('accept', '')
    
    if 'application/json' in accept:
        return 'json'
    elif 'text/html' in accept:
        return 'html'
    elif 'application/xml' in accept:
        return 'xml'
    elif 'application/raw' in accept:
        return 'raw'
    else:
        return 'html'  # default


class DefaultRenderer:
    """Base renderer that handles Accept header content negotiation."""
    
    def render(self, request: Request, **kwargs) -> Union[HiccupTree, Dict[str, Any]]:
        """Main entry point - delegates based on Accept header with UI as default."""
        format_to_render_func = {
            'json': lambda: self.component_to_json(self.render_api(**kwargs)),
            'html': lambda: self.render_ui(**kwargs),
            'xml': lambda: self.render_api(**kwargs),
            'raw': lambda: self.render_raw(**kwargs),
        }
        
        _format = get_preferred_format(request)
        return format_to_render_func[_format]()
    
    def render_ui(self, request: Request, **kwargs) -> HiccupTree:
        """Override in subclasses for full page HTML."""
        raise NotImplementedError("Subclasses must implement render_ui")
        
    def render_api(self, request: Request, **kwargs) -> HiccupTree:
        """Default: fall back to UI rendering if no specific API version needed."""
        return self.render_ui(**kwargs)
        
    def render_raw(self, request: Request, **kwargs) -> str:
        """Identity renderer for debugging - returns raw data as string."""
        import json
        return json.dumps(kwargs, indent=2, default=str)
    
    def component_to_json(self, component: HiccupTree) -> Union[Dict[str, Any], Any]:
        """Convert hiccup-style web component to JSON representation."""
        if isinstance(component, list) and len(component) >= 2:
            tag = component[0]
            attrs = component[1] if len(component) > 1 and isinstance(component[1], dict) else {}
            children = component[2:] if len(component) > 2 else []
            
            # Handle case where no attributes dict exists
            if len(component) > 1 and not isinstance(component[1], dict):
                children = component[1:]
                attrs = {}
            
            result = {
                "component": tag,
                "attributes": attrs
            }
            
            if children:
                # Recursively convert children
                result["children"] = [
                    self.component_to_json(child) if isinstance(child, list) 
                    else child  # Plain text/strings stay as-is
                    for child in children
                ]
            
            return result
        else:
            return component  # Plain text or other primitives


class UIRenderer(HiccupRenderer):
    """Renders components for browser clients with rich UI."""
    pass  # Uses base HiccupRenderer behavior


class ApiRenderer(HiccupRenderer):
    """Renders components for API clients - same as UI since web components handle both contexts."""
    pass  # Uses base HiccupRenderer behavior - web components are universal
