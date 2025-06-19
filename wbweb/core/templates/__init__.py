"""
Core template framework module.

Provides hiccup-style rendering and content negotiation.
"""

from .hiccup import HiccupRenderer, HiccupTree

__all__ = ["HiccupRenderer", "HiccupTree"]