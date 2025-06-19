"""
Core database framework module.

Provides Django-style SQLAlchemy managers, base classes, and database configuration.
"""

from .managers import Manager, configure_session_maker
from .base import Base, BaseMeta
from .config import (
    configure_database, 
    get_engine, 
    get_async_session_maker, 
    create_tables, 
    drop_tables, 
    get_db_session,
    get_session_for_managers
)

__all__ = [
    "Manager", "configure_session_maker", "Base", "BaseMeta",
    "configure_database", "get_engine", "get_async_session_maker", 
    "create_tables", "drop_tables", "get_db_session", "get_session_for_managers"
]