"""
SQLAlchemy base classes with Django-style manager support.

Provides base classes for all database models with automatic manager setup.
"""

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from .managers import Manager


class BaseMeta(type(DeclarativeBase)):
    """
    Metaclass that combines DeclarativeBase metaclass with Django-style manager setup.
    """
    
    def __new__(mcs, name, bases, namespace, **kwargs):
        # Let DeclarativeBase handle its logic first
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        
        # Only process actual model classes (ones with __tablename__ and no __no_table__)
        if hasattr(cls, '__tablename__') and not getattr(cls, '__no_table__', False):
            # Find managers in the class and bind them
            for attr_name, attr_value in namespace.items():
                if isinstance(attr_value, Manager):
                    # Replace with bound manager
                    setattr(cls, attr_name, Manager(cls))
            
            # Always provide default 'objects' manager (Django behavior)
            # This happens automatically even if not declared in class
            if not hasattr(cls, 'objects'):
                cls.objects = Manager(cls)
        
        return cls


class Base(AsyncAttrs, DeclarativeBase, metaclass=BaseMeta):
    """Base class for all SQLAlchemy models with Django-style manager setup."""
    pass