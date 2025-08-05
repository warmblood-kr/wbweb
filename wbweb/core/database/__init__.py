"""
Core database framework module.

Provides Django-style SQLAlchemy managers and base classes.
For database engines, use engine_factory directly.
"""

from .managers import Manager, get_session
from .base import Base, BaseMeta
from .session_context import session_context

__all__ = [
    "Manager", "get_session", "Base", "BaseMeta", "session_context"
]