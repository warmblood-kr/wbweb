"""
Django-style managers and session management for SQLAlchemy ORM.

Provides Django-like API (Model.objects.create(), Model.objects.filter()) 
while handling SQLAlchemy session management automatically.
"""

from functools import wraps
from typing import Any, Dict, List, Optional, Type, TypeVar, Callable
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')

async def get_session() -> AsyncSession:
    """
    Get a database session from engine_factory.
    
    This provides both high-level Manager operations and low-level session access.
    Use with async context manager for proper cleanup.
    
    Example:
        async with get_session() as session:
            session.add(User(name="John"))
            await session.commit()
    """
    from ..config import settings
    from .engine_factory import engine_factory
    from sqlalchemy.ext.asyncio import async_sessionmaker
    
    engine = engine_factory.create_engine(settings.DATABASE_URL)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    return session_maker()


# Remove complex @with_session decorator - using simpler approach


class Manager:
    """
    Django-style manager for SQLAlchemy models.
    
    Provides methods like create(), get(), filter() that automatically
    handle session management and provide Django-like API.
    """
    
    def __init__(self, model_class: Optional[Type[T]] = None):
        self.model_class = model_class
    
    async def create(self, **kwargs) -> T:
        """
        Create and save a new model instance.
        
        Similar to Django's Model.objects.create(**kwargs)
        """
        async with get_session() as session:
            instance = self.model_class(**kwargs)
            session.add(instance)
            await session.flush()  # Get ID without committing transaction
            await session.refresh(instance)
            await session.commit()  # Auto-commit like Django
            return instance
    
    async def get(self, **kwargs) -> Optional[T]:
        """
        Get a single model instance matching the given criteria.
        
        Similar to Django's Model.objects.get(**kwargs)
        Returns None if not found (unlike Django which raises exception).
        """
        async with get_session() as session:
            stmt = select(self.model_class)
            for key, value in kwargs.items():
                stmt = stmt.where(getattr(self.model_class, key) == value)
            
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def filter(self, **kwargs) -> List[T]:
        """
        Get all model instances matching the given criteria.
        
        Similar to Django's Model.objects.filter(**kwargs).all()
        """
        async with get_session() as session:
            stmt = select(self.model_class)
            for key, value in kwargs.items():
                stmt = stmt.where(getattr(self.model_class, key) == value)
            
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def all(self) -> List[T]:
        """
        Get all model instances.
        
        Similar to Django's Model.objects.all()
        """
        async with get_session() as session:
            stmt = select(self.model_class)
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def get_or_create(self, defaults: Optional[Dict[str, Any]] = None, **kwargs) -> tuple[T, bool]:
        """
        Get an instance or create it if it doesn't exist.
        
        Similar to Django's Model.objects.get_or_create()
        Returns (instance, created) tuple.
        """
        # Check if exists first
        instance = await self.get(**kwargs)
        if instance:
            return instance, False
        
        # Create new instance with defaults
        create_kwargs = kwargs.copy()
        if defaults:
            create_kwargs.update(defaults)
        
        instance = await self.create(**create_kwargs)
        return instance, True