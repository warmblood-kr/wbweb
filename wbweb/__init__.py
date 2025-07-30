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
from wbweb.core.templates import HiccupRenderer, HiccupTree, DefaultRenderer, UIRenderer, ApiRenderer
from wbweb.core.templates.hiccup import raw
from wbweb.core.web import renderer, content_negotiation, render_error_response
from wbweb.core.database import (
    Manager, configure_session_maker, Base, BaseMeta
)

__all__ = [
    "HiccupRenderer", "HiccupTree", "DefaultRenderer", "UIRenderer", "ApiRenderer", "raw",
    "renderer", "content_negotiation", "render_error_response",
    "Manager", "configure_session_maker", "Base", "BaseMeta"
]