"""
Decorators for web layer framework.

Provides reusable decorators for cross-cutting concerns like content negotiation.
"""

from functools import wraps
from starlette.responses import HTMLResponse
from starlette.requests import Request
from .negotiation import ContentNegotiator


def content_negotiation(renderer_class):
    """
    Decorator that uses a domain-specific renderer for content negotiation.
    
    Args:
        renderer_class: A class that inherits from DefaultRenderer
    
    Usage:
        @content_negotiation(MyRenderer)
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
    if ContentNegotiator.is_api_request(request):
        return HTMLResponse(api_message, status_code=status_code)
    else:
        return HTMLResponse(ui_html, status_code=status_code)