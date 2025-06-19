"""
Template rendering framework for wbweb.

Provides hiccup-style HTML rendering and content negotiation.
"""

from .hiccup import HiccupRenderer, HiccupTree

__all__ = ["HiccupRenderer", "HiccupTree"]