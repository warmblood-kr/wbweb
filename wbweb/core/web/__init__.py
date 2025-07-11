"""
Web framework components for content negotiation and request handling.
"""

from .decorators import renderer, content_negotiation, render_error_response

__all__ = ['renderer', 'content_negotiation', 'render_error_response']