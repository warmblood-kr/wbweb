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

# Global session maker - can be configured by the application
_session_maker: Optional[Callable[[], AsyncSession]] = None


def configure_session_maker(session_maker: Callable[[], AsyncSession]):
    """
    Configure the session maker for all managers.
    
    This should be called once during application startup to provide
    the async session maker that managers will use.
    
    Args:
        session_maker: Callable that returns an AsyncSession context manager
    """
    global _session_maker
    _session_maker = session_maker


def get_session_maker() -> Callable[[], AsyncSession]:
    """
    Get the configured session maker.
    
    Raises:
        RuntimeError: If no session maker has been configured
    """
    if _session_maker is None:
        raise RuntimeError(
            "No session maker configured. Call configure_session_maker() "
            "during application startup to provide an async session maker."
        )
    return _session_maker


def with_session(func):
    """
    Decorator that provides automatic session management for model operations.
    
    Handles session creation, commit, rollback, and cleanup automatically,
    similar to Django's ORM transaction management.
    """
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        session_maker = get_session_maker()
        async with session_maker() as session:
            # Inject session into manager temporarily
            old_session = getattr(self, '_session', None)
            self._session = session
            try:
                result = await func(self, *args, **kwargs)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
            finally:
                # Restore previous session state
                self._session = old_session
    return wrapper


class Manager:
    """
    Django-style manager for SQLAlchemy models.
    
    Provides methods like create(), get(), filter() that automatically
    handle session management and provide Django-like API.
    """
    
    def __init__(self, model_class: Optional[Type[T]] = None):
        self.model_class = model_class
        self._session: Optional[AsyncSession] = None
    
    @with_session
    async def create(self, **kwargs) -> T:
        """
        Create and save a new model instance.
        
        Similar to Django's Model.objects.create(**kwargs)
        """
        instance = self.model_class(**kwargs)
        self._session.add(instance)
        await self._session.flush()  # Get ID without committing transaction
        await self._session.refresh(instance)
        return instance
    
    @with_session
    async def get(self, **kwargs) -> Optional[T]:
        """
        Get a single model instance matching the given criteria.
        
        Similar to Django's Model.objects.get(**kwargs)
        Returns None if not found (unlike Django which raises exception).
        """
        stmt = select(self.model_class)
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model_class, key) == value)
        
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    @with_session  
    async def filter(self, **kwargs) -> List[T]:
        """
        Get all model instances matching the given criteria.
        
        Similar to Django's Model.objects.filter(**kwargs).all()
        """
        stmt = select(self.model_class)
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model_class, key) == value)
        
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    @with_session
    async def all(self) -> List[T]:
        """
        Get all model instances.
        
        Similar to Django's Model.objects.all()
        """
        stmt = select(self.model_class)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    @with_session
    async def get_or_create(self, defaults: Optional[Dict[str, Any]] = None, **kwargs) -> tuple[T, bool]:
        """
        Get an instance or create it if it doesn't exist.
        
        Similar to Django's Model.objects.get_or_create()
        Returns (instance, created) tuple.
        """
        instance = await self.get(**kwargs)
        if instance:
            return instance, False
        
        # Create new instance with defaults
        create_kwargs = kwargs.copy()
        if defaults:
            create_kwargs.update(defaults)
        
        instance = await self.create(**create_kwargs)
        return instance, True