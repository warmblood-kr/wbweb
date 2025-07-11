"""
Web framework components for content negotiation and request handling.
"""

from .decorators import content_negotiation, render_error_response

__all__ = ['content_negotiation', 'render_error_response']