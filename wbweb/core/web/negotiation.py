"""
Content negotiation for dual API/UI responses.

Handles detection of API clients vs browser clients to serve appropriate
response formats using strategy pattern for renderers.
"""

from starlette.requests import Request
from ..templates import UIRenderer, ApiRenderer


class ContentNegotiator:
    """Handles content negotiation between API and UI responses using strategy pattern."""
    
    @staticmethod
    def is_api_request(request: Request) -> bool:
        """
        Determine if request is from API client or browser.
        
        API clients are identified by X-API-Client header.
        HTMX requests (for form submissions) are treated as API requests for component-only responses.
        """
        return (request.headers.get('x-api-client') is not None or 
                request.headers.get('hx-request') is not None)
    
    @staticmethod
    def get_renderer(request: Request):
        """
        Get appropriate renderer based on request type.
        
        Returns ApiRenderer for API clients and HTMX requests, UIRenderer for browsers.
        """
        if ContentNegotiator.is_api_request(request):
            return ApiRenderer()
        return UIRenderer()