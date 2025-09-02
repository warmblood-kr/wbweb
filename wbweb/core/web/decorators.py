"""
Decorators for web layer framework.

Provides reusable decorators for cross-cutting concerns like content negotiation.
"""

import json
import warnings
from functools import wraps

from starlette.responses import HTMLResponse, RedirectResponse, Response
from starlette.requests import Request
from starlette.datastructures import URL

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
            result_dict = await view_func(request)

            redirect_url = result_dict.get('redirect_url', '')

            if redirect_url:
                if not request.headers.get('HX-Request'):
                    return RedirectResponse(redirect_url, status_code=303)

                url = redirect_url

                if isinstance(redirect_url, URL):
                    url = redirect_url.path if redirect_url.hostname == request.url.hostname \
                        else str(redirect_url)

                response = Response(status_code=200)
                response.headers['HX-Redirect'] = url
                return response

            renderer = renderer_class()
            data = renderer.render(request, **result_dict)
            return Response(**data)

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
