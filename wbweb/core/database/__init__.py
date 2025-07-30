"""
Core database framework module.

Provides Django-style SQLAlchemy managers and base classes.
For database engines, use engine_factory directly.
"""

from .managers import Manager, configure_session_maker
from .base import Base, BaseMeta

__all__ = [
    "Manager", "configure_session_maker", "Base", "BaseMeta"
]