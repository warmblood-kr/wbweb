"""
Django-style managers and session management for SQLAlchemy ORM.

Provides Django-like API (Model.objects.create(), Model.objects.filter()) 
while handling SQLAlchemy session management automatically.
"""

from functools import wraps
from typing import Any, Dict, List, Optional, Type, TypeVar, Callable
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')

class ORMException(Exception): ...
class DoesNotExist(ORMException): ...


class AsyncQuerySet:
    """
    Lazy query builder that behaves like List[T] when awaited.
    
    Enables method chaining (.filter().options()) while maintaining
    backwards compatibility with existing code that expects List[T].
    """
    
    def __init__(self, model_class: Type[T], session_factory):
        self.model_class = model_class
        self.session_factory = session_factory
        self._stmt = select(model_class)
        self._result_cache = None
    
    def _clone(self) -> 'AsyncQuerySet':
        """Create a copy of this QuerySet for method chaining."""
        new_qs = AsyncQuerySet(self.model_class, self.session_factory)
        new_qs._stmt = self._stmt
        return new_qs
    
    def filter(self, **kwargs) -> 'AsyncQuerySet':
        """Add WHERE conditions. Returns new QuerySet for chaining."""
        new_qs = self._clone()
        for key, value in kwargs.items():
            new_qs._stmt = new_qs._stmt.where(getattr(self.model_class, key) == value)
        return new_qs
    
    def options(self, *opts) -> 'AsyncQuerySet':
        """Add SQLAlchemy loading options (joinedload, selectinload, etc)."""
        new_qs = self._clone()
        new_qs._stmt = new_qs._stmt.options(*opts)
        return new_qs
    
    async def _fetch_all(self) -> List[T]:
        """Execute query and return all results."""
        session = await self.session_factory()
        async with session:
            result = await session.execute(self._stmt)
            return list(result.scalars().all())
    
    def __await__(self):
        """Make QuerySet awaitable. Caches results for list-like behavior."""
        async def _await():
            if self._result_cache is None:
                self._result_cache = await self._fetch_all()
            return self._result_cache
        return _await().__await__()
    
    async def __aiter__(self):
        """Support async iteration: async for item in queryset"""
        if self._result_cache is None:
            self._result_cache = await self._fetch_all()
        for item in self._result_cache:
            yield item


async def get_session() -> AsyncSession:
    """
    Get a database session from engine_factory.
    
    Enhanced to support optional session context sharing while maintaining
    full backward compatibility. If a context session is active, returns that.
    Otherwise, creates a new session as before.
    
    This provides both high-level Manager operations and low-level session access.
    Use with async context manager for proper cleanup.
    
    Example:
        session = await get_session()
        async with session:
            session.add(User(name="John"))
            await session.commit()
    """
    # Check for context session first (new optional feature)
    try:
        from .session_context import get_context_session
        context_session = get_context_session()
        if context_session is not None:
            return context_session
    except ImportError:
        # If session_context module is not available, continue with old behavior
        pass
    
    # Original behavior - create new session (unchanged)
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
        session = await get_session()
        async with session:
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
        session = await get_session()
        async with session:
            stmt = select(self.model_class)
            for key, value in kwargs.items():
                stmt = stmt.where(getattr(self.model_class, key) == value)
            
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            if obj is None:
                raise DoesNotExist()
            return obj

    def filter(self, **kwargs) -> AsyncQuerySet:
        """
        Get model instances matching the given criteria.
        
        Returns AsyncQuerySet for method chaining (.filter().options()).
        Awaiting the result gives List[T] for backwards compatibility.
        """
        qs = AsyncQuerySet(self.model_class, get_session)
        return qs.filter(**kwargs)
    
    def all(self) -> AsyncQuerySet:
        """
        Get all model instances.
        
        Returns AsyncQuerySet. Await the result to get List[T].
        """
        return AsyncQuerySet(self.model_class, get_session)
    
    async def get_or_create(self, defaults: Optional[Dict[str, Any]] = None, **kwargs) -> tuple[T, bool]:
        """
        Get an instance or create it if it doesn't exist.
        
        Similar to Django's Model.objects.get_or_create()
        Returns (instance, created) tuple.
        """
        # Check if exists first
        try:
            instance = await self.get(**kwargs)
            return instance, False
        except DoesNotExist:
            # Create new instance with defaults
            create_kwargs = kwargs.copy()
            if defaults:
                create_kwargs.update(defaults)

            instance = await self.create(**create_kwargs)
            return instance, True
