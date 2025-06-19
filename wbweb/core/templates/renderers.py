"""
Renderer strategy classes for different client types.

Provides format-specific rendering following DRF-style renderer pattern.
"""

from typing import Any, Dict, List, Union
from starlette.requests import Request
from .hiccup import HiccupRenderer, HiccupTree


class DefaultRenderer:
    """Base renderer that handles Accept header content negotiation."""
    
    def render(self, request: Request, **kwargs) -> Union[HiccupTree, Dict[str, Any]]:
        """Main entry point - delegates based on Accept header with UI as default."""
        accept = request.headers.get('accept', '')
        
        # Check for backward compatibility API indicators
        is_legacy_api_client = (
            request.headers.get('x-api-client') is not None or 
            request.headers.get('hx-request') is not None
        )
        
        if 'application/json' in accept:
            # Always use component-based JSON for consistency
            component = self.render_api(**kwargs)
            return self.component_to_json(component)
        elif 'text/html' in accept:
            # Browsers requesting HTML (primary preference)
            return self.render_ui(**kwargs)
        elif 'application/xml' in accept or is_legacy_api_client:
            # XML/HTML components for API clients (including legacy headers)
            return self.render_api(**kwargs)
        elif 'application/raw' in accept:
            # Raw/identity renderer for debugging
            return self.render_raw(**kwargs)
        else:
            # Default to UI rendering (no Accept header, etc.)
            return self.render_ui(**kwargs)
    
    def render_ui(self, **kwargs) -> HiccupTree:
        """Override in subclasses for full page HTML."""
        raise NotImplementedError("Subclasses must implement render_ui")
        
    def render_api(self, **kwargs) -> HiccupTree:
        """Default: fall back to UI rendering if no specific API version needed."""
        return self.render_ui(**kwargs)
        
    def render_raw(self, **kwargs) -> str:
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