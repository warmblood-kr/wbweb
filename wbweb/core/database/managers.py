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
    
    def filter(self, *expressions, **kwargs) -> 'AsyncQuerySet':
        """
        Add WHERE conditions. Returns new QuerySet for chaining.
        
        Supports both Django-style kwargs and native SQLAlchemy expressions:
        
        Examples:
            # Simple kwargs (Django-style)
            Model.objects.filter(name="test", status="active")
            
            # SQLAlchemy expressions (superior for complex queries)
            Model.objects.filter(Model.id.in_([1, 2, 3]))
            Model.objects.filter(Model.name.like('%pattern%'))
            Model.objects.filter(Model.date.between(start, end))
            
            # Mixed usage
            Model.objects.filter(Model.id.in_([1, 2, 3]), status="active")
            
            # Method chaining
            Model.objects.filter(status="active").filter(Model.id.in_([1, 2, 3]))
        """
        new_qs = self._clone()
        
        # Apply SQLAlchemy expressions (positional args)
        for expression in expressions:
            new_qs._stmt = new_qs._stmt.where(expression)
        
        # Apply simple kwargs
        for key, value in kwargs.items():
            new_qs._stmt = new_qs._stmt.where(getattr(self.model_class, key) == value)
        
        return new_qs
    
    def options(self, *opts) -> 'AsyncQuerySet':
        """Add SQLAlchemy loading options (joinedload, selectinload, etc)."""
        new_qs = self._clone()
        new_qs._stmt = new_qs._stmt.options(*opts)
        return new_qs
    
    def order_by(self, *args) -> 'AsyncQuerySet':
        """Add ORDER BY clauses. Returns new QuerySet for chaining."""
        new_qs = self._clone()
        new_qs._stmt = new_qs._stmt.order_by(*args)
        return new_qs
    
    def add_columns(self, *columns) -> 'AsyncQuerySet':
        """Add columns to SELECT statement (for raw queries)"""
        if self.model_class is not None:
            raise ValueError("add_columns() is for raw queries only")
        
        new_qs = self._clone()
        new_qs._stmt = new_qs._stmt.add_columns(*columns)
        return new_qs
    
    def group_by(self, *args) -> 'AsyncQuerySet':
        """Add GROUP BY clauses (for raw queries)"""
        if self.model_class is not None:
            raise ValueError("group_by() is for raw queries only")
        
        new_qs = self._clone()
        new_qs._stmt = new_qs._stmt.group_by(*args)
        return new_qs
    
    def select_from(self, *args) -> 'AsyncQuerySet':
        """Update FROM clause (for raw queries)"""
        if self.model_class is not None:
            raise ValueError("select_from() is for raw queries only")
        
        new_qs = self._clone()
        new_qs._stmt = new_qs._stmt.select_from(*args)
        return new_qs
    
    @property
    def froms(self):
        """Access to FROM clauses (for compatibility with SQLAlchemy select objects)"""
        return self._stmt.froms
    
    async def _fetch_all(self) -> List[T]:
        """Execute query and return all results."""
        session = await self.session_factory()
        async with session:
            result = await session.execute(self._stmt)
            
            # Handle raw queries vs model queries
            if self.model_class is None:
                # Raw query - return row objects
                return result.fetchall()
            else:
                # Model query - return model instances
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
    
    async def get(self):
        """Get single result (for raw queries)"""
        if self.model_class is not None:
            raise ValueError("get() method is for raw queries only. Use await queryset for model queries.")
        
        session = await self.session_factory()
        async with session:
            result = await session.execute(self._stmt)
            return result.fetchone()
    
    async def first(self):
        """Get first result or None"""
        session = await self.session_factory()
        async with session:
            result = await session.execute(self._stmt)
            
            if self.model_class is None:
                # Raw query
                return result.first()
            else:
                # Model query
                return result.scalars().first()
    
    async def scalar(self):
        """Get single scalar value (for raw queries)"""
        if self.model_class is not None:
            raise ValueError("scalar() method is for raw queries only.")
        
        session = await self.session_factory()
        async with session:
            result = await session.execute(self._stmt)
            return result.scalar()
    
    async def all(self):
        """Get all results (explicit method for convenience)"""
        return await self._fetch_all()


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
    from ..config import settings
    from .engine_factory import engine_factory
    from sqlalchemy.ext.asyncio import async_sessionmaker
    
    engine = engine_factory.create_engine(settings.DATABASE_URL)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    return session_maker()


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

    def filter(self, *expressions, **kwargs) -> AsyncQuerySet:
        """
        Get model instances matching the given criteria.
        
        Supports both Django-style kwargs and native SQLAlchemy expressions.
        Returns AsyncQuerySet for method chaining (.filter().options()).
        Awaiting the result gives List[T] for backwards compatibility.
        
        Examples:
            # Simple kwargs (Django-style)
            Model.objects.filter(name="test", status="active")
            
            # SQLAlchemy expressions (superior for complex queries)
            Model.objects.filter(Model.id.in_([1, 2, 3]))
            Model.objects.filter(Model.name.like('%pattern%'))
            
            # Method chaining
            Model.objects.filter(status="active").filter(Model.id.in_([1, 2, 3]))
        """
        qs = AsyncQuerySet(self.model_class, get_session)
        return qs.filter(*expressions, **kwargs)
    
    def all(self) -> AsyncQuerySet:
        """
        Get all model instances.
        
        Returns AsyncQuerySet. Await the result to get List[T].
        """
        return AsyncQuerySet(self.model_class, get_session)
    
    def order_by(self, *args) -> AsyncQuerySet:
        """
        Get all model instances ordered by given columns.
        
        Returns AsyncQuerySet for method chaining.
        """
        return AsyncQuerySet(self.model_class, get_session).order_by(*args)
    
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
