"""
Renderer strategy classes for different client types.

Provides format-specific rendering following DRF-style renderer pattern.
"""

import json
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
    elif 'application/xml' in accept or 'text/xml' in accept:
        return 'xml'
    elif 'application/raw' in accept:
        return 'raw'
    else:
        return 'html'  # default


def parse_accept_header(accept_header_value: str):
    if not accept_header_value:
        return []

    media_types = []
    for part in accept_header_value.split(','):
        sub_parts = part.strip().split(';')
        media_type = sub_parts[0].strip()
        q_value = 1.0
        for s in sub_parts[1:]:
            if s.strip().startswith('q='):
                try:
                    q_value = float(s.strip()[2:])
                except ValueError:
                    pass
        media_types.append((media_type, q_value))
    media_types.sort(key=lambda x: x[1], reverse=True)
    return media_types


class DefaultRenderer:
    """Base renderer that handles Accept header content negotiation."""
    
    def render(self, request: Request, **kwargs) -> Dict[str, Any]:
        """Main entry point - delegates based on Accept header with UI as default."""
        accept_header_value = request.headers.get('accept', 'text/html')
        accept = parse_accept_header(accept_header_value)[0][0]

        render_func = {
            'application/json': lambda: json.dumps(self.render_api(request, **kwargs)),
            'text/html': lambda: HiccupRenderer().render(self.render_ui(request, **kwargs)),
            'text/xml': lambda: json.dumps(self.render_api(request, **kwargs)),
            'application/xml': lambda: json.dumps(self.render_api(request, **kwargs)),
            'application/raw': lambda: self.render_raw(request, **kwargs),
        }.get(accept, lambda: '')

        return {'content': render_func(), 'media_type': accept, 'status_code': 200}

    def render_ui(self, request: Request, **kwargs) -> HiccupTree:
        """Override in subclasses for full page HTML."""
        return []

    def render_api(self, request: Request, **kwargs) -> HiccupTree:
        """Default: fall back to UI rendering if no specific API version needed."""
        return self.render_ui(**kwargs)
        
    def render_raw(self, request: Request, **kwargs) -> str:
        """Identity renderer for debugging - returns raw data as string."""
        return kwargs


class UIRenderer(HiccupRenderer):
    """Renders components for browser clients with rich UI."""
    pass  # Uses base HiccupRenderer behavior


class ApiRenderer(HiccupRenderer):
    """Renders components for API clients - same as UI since web components handle both contexts."""
    pass  # Uses base HiccupRenderer behavior - web components are universal
