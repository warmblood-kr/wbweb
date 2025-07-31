"""
SQLAlchemy base classes with Django-style manager support.

Provides base classes for all database models with automatic manager setup.
"""

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from .managers import Manager, get_session


class BaseMeta(type(DeclarativeBase)):
    """
    Metaclass that combines DeclarativeBase metaclass with Django-style manager setup.
    """
    
    def __new__(mcs, name, bases, namespace, **kwargs):
        # Let DeclarativeBase handle its logic first
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        
        for attr_name, attr_value in namespace.items():
            if isinstance(attr_value, Manager):
                # Replace with bound manager of the same type
                manager_class = type(attr_value)
                setattr(cls, attr_name, manager_class(cls))
        
        # Only process actual model classes (ones with __tablename__ and no __no_table__)
        if hasattr(cls, '__tablename__') and not getattr(cls, '__no_table__', False):
            # Always provide default 'objects' manager (Django behavior)
            # This happens automatically even if not declared in class
            if not hasattr(cls, 'objects'):
                cls.objects = Manager(cls)
        
        return cls


class Base(AsyncAttrs, DeclarativeBase, metaclass=BaseMeta):
    """Base class for all SQLAlchemy models with Django-style manager setup."""
    
    async def save(self):
        """
        Django-style save method for model instances.
        Uses SQLAlchemy's merge() which automatically handles both INSERT and UPDATE.
        """
        session = await get_session()
        async with session:
            merged = await session.merge(self)
            await session.flush()
            # Update self with merged values to reflect any DB changes
            for attr_name in self.__table__.columns.keys():
                setattr(self, attr_name, getattr(merged, attr_name))
            await session.commit()  # Auto-commit like Django
            return self
