"""
Database configuration and session management.

Provides async SQLAlchemy engine and session management with configurable settings.
"""

import os
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine
from .base import Base

# Global configuration - can be set by the application
_database_config: Optional[Dict[str, Any]] = None
_engine: Optional[AsyncEngine] = None
_session_maker: Optional[async_sessionmaker] = None


def configure_database(database_url: str, debug: bool = False, **engine_kwargs) -> None:
    """
    Configure the database connection for the application.
    
    This should be called once during application startup to provide
    the database configuration that the framework will use.
    
    Args:
        database_url: SQLAlchemy database URL (e.g., 'sqlite+aiosqlite:///./test.db')
        debug: Whether to echo SQL queries for debugging
        **engine_kwargs: Additional keyword arguments for create_async_engine
    """
    global _database_config, _engine, _session_maker
    
    _database_config = {
        'database_url': database_url,
        'debug': debug,
        'engine_kwargs': engine_kwargs
    }
    
    # Reset engine and session maker to force recreation
    _engine = None
    _session_maker = None


def get_database_config() -> Dict[str, Any]:
    """
    Get the current database configuration.
    
    Raises:
        RuntimeError: If no database configuration has been set
    """
    if _database_config is None:
        raise RuntimeError(
            "No database configuration set. Call configure_database() "
            "during application startup to provide database settings."
        )
    return _database_config


def get_engine() -> AsyncEngine:
    """Get database engine with appropriate configuration."""
    global _engine
    
    if _engine is None:
        config = get_database_config()
        database_url = config['database_url']
        debug = config['debug']
        engine_kwargs = config.get('engine_kwargs', {})
        
        # Configure engine based on database type and environment
        connect_args = {}
        echo = debug  # Echo SQL queries in debug mode
        
        # SQLite-specific configuration
        if "sqlite" in database_url:
            connect_args = {"check_same_thread": False}
        
        # PostgreSQL-specific configuration  
        elif "postgresql" in database_url:
            # Add any PostgreSQL-specific settings here
            pass
        
        # Merge connect_args with any provided engine_kwargs
        final_kwargs = {
            'echo': echo,
            'connect_args': connect_args,
            **engine_kwargs
        }
        
        # Use engine factory for enhanced database engine creation
        from .engine_factory import engine_factory
        _engine = engine_factory.create_engine(database_url)
    
    return _engine


def get_async_session_maker() -> async_sessionmaker:
    """Get the configured async session maker."""
    global _session_maker
    
    if _session_maker is None:
        engine = get_engine()
        _session_maker = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
    
    return _session_maker


async def create_tables():
    """Create all database tables."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop all database tables (for testing)."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_db_session() -> AsyncSession:
    """Get a database session."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


# Convenience function to get a session for use with managers
def get_session_for_managers():
    """Get session maker function for use with Manager.configure_session_maker()."""
    return get_async_session_maker()