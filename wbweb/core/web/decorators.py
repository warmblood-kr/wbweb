"""
Decorators for web layer framework.

Provides reusable decorators for cross-cutting concerns like content negotiation.
"""

import warnings
from functools import wraps
from starlette.responses import HTMLResponse, RedirectResponse, Response
from starlette.requests import Request
from ..templates.renderers import get_preferred_format


def renderer(renderer_class):
    """
    Decorator that wires a view function to a domain-specific renderer.
    
    Args:
        renderer_class: A class that inherits from DefaultRenderer
    
    Usage:
        @renderer(MyRenderer)
        async def my_endpoint(request):
            return {'data': my_data, 'status_code': 200}
    """
    
    def decorator(view_func):
        @wraps(view_func)
        async def wrapper(request):
            # Call the view function to get result dict
            result_dict = await view_func(request)
            
            # Create domain-specific renderer instance
            renderer = renderer_class()
            
            # Let renderer handle content negotiation based on Accept header
            component_or_data = renderer.render(request, **result_dict)
            
            redirect_url = result_dict.get('redirect_url', '')

            if redirect_url:
                if request.headers.get('HX-Request'):
                    response = Response(status_code=200)
                    response.headers['HX-Redirect'] = redirect_url
                    return response
                    
                return RedirectResponse(redirect_url, status_code=303)
            
            # Handle different return types
            if isinstance(component_or_data, dict):
                # JSON response - business data already serialized
                import json
                json_str = json.dumps(component_or_data)
                return HTMLResponse(json_str, status_code=result_dict.get('status_code', 200))
            else:
                # HTML/XML component response
                from ..templates.hiccup import HiccupRenderer
                hiccup_renderer = HiccupRenderer()
                html = hiccup_renderer.render(component_or_data)
                
                # Return HTML response
                status_code = result_dict.get('status_code', 200)
                
                return HTMLResponse(html, status_code=status_code)
        
        return wrapper
    return decorator



def render_error_response(request: Request, api_message: str, ui_html: str, status_code: int) -> HTMLResponse:
    """
    Helper function for exception handlers to apply content negotiation.
    
    Args:
        request: The request object
        api_message: Simple message for API clients
        ui_html: Rich HTML for browser clients
        status_code: HTTP status code
    
    Returns:
        HTMLResponse with appropriate content based on client type
    """
    preferred_format = get_preferred_format(request)
    
    if preferred_format in ['json', 'xml', 'raw']:
        return HTMLResponse(api_message, status_code=status_code)
    
    return HTMLResponse(ui_html, status_code=status_code)


def content_negotiation(renderer_class):
    """
    DEPRECATED: Use @renderer decorator instead.
    
    This decorator is deprecated and will be removed in a future version.
    Use @renderer(renderer_class) instead.
    
    Args:
        renderer_class: A class that inherits from DefaultRenderer
    
    Returns:
        The same decorator as @renderer but with deprecation warning
    """
    warnings.warn(
        "@content_negotiation is deprecated. Use @renderer instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return renderer(renderer_class)
