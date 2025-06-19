"""
wbweb - A general-purpose web framework for Warmblood Co., Ltd.

Core Features:
- Hiccup-style HTML rendering (Python data structures → HTML)
- Content negotiation (automatic API/UI client detection)
- Django-style SQLAlchemy managers with async support
- Generic configuration system
- Minimal dependencies (Starlette + SQLAlchemy)
"""

__version__ = "0.1.0"

# Main exports for convenience
from wbweb.core.templates import HiccupRenderer, HiccupTree

__all__ = ["HiccupRenderer", "HiccupTree"]