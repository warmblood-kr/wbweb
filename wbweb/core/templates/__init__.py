"""
Core template framework module.

Provides hiccup-style rendering and content negotiation.
"""

from .hiccup import HiccupRenderer, HiccupTree
from .renderers import DefaultRenderer, UIRenderer, ApiRenderer

__all__ = ["HiccupRenderer", "HiccupTree", "DefaultRenderer", "UIRenderer", "ApiRenderer"]