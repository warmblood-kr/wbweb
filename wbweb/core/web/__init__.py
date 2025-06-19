"""
Web framework components for content negotiation and request handling.
"""

from .negotiation import ContentNegotiator
from .decorators import content_negotiation, render_error_response

__all__ = ['ContentNegotiator', 'content_negotiation', 'render_error_response']