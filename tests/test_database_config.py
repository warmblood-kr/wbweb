"""
Test database configuration and session management.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker


class TestDatabaseConfigImports:
    """Test that database config functions can be imported correctly."""
    
    def test_import_from_database_module(self):
        """Test importing config functions from database module."""
        from wbweb.core.database import (
            configure_database, get_engine, get_async_session_maker,
            create_tables, drop_tables, get_db_session
        )
        assert configure_database is not None
        assert get_engine is not None
        assert get_async_session_maker is not None
        assert create_tables is not None
        assert drop_tables is not None
        assert get_db_session is not None
        
    def test_import_from_main_package(self):
        """Test importing from main wbweb package."""
        from wbweb import (
            configure_database, get_engine, get_async_session_maker,
            create_tables, drop_tables, get_db_session
        )
        assert configure_database is not None
        assert get_engine is not None
        assert get_async_session_maker is not None
        assert create_tables is not None
        assert drop_tables is not None
        assert get_db_session is not None


class TestDatabaseConfiguration:
    """Test database configuration system."""
    
    def setup_method(self):
        """Reset configuration before each test."""
        import wbweb.core.database.config
        # Reset global state
        wbweb.core.database.config._database_config = None
        wbweb.core.database.config._engine = None
        wbweb.core.database.config._session_maker = None
    
    def test_configure_database_basic(self):
        """Test basic database configuration."""
        from wbweb.core.database.config import configure_database, get_database_config
        
        configure_database("sqlite+aiosqlite:///./test.db", debug=True)
        
        config = get_database_config()
        assert config['database_url'] == "sqlite+aiosqlite:///./test.db"
        assert config['debug'] is True
        assert config['engine_kwargs'] == {}
    
    def test_configure_database_with_engine_kwargs(self):
        """Test database configuration with additional engine arguments."""
        from wbweb.core.database.config import configure_database, get_database_config
        
        configure_database(
            "postgresql+asyncpg://user:pass@localhost/db",
            debug=False,
            pool_size=20,
            max_overflow=30
        )
        
        config = get_database_config()
        assert config['database_url'] == "postgresql+asyncpg://user:pass@localhost/db"
        assert config['debug'] is False
        assert config['engine_kwargs'] == {'pool_size': 20, 'max_overflow': 30}
    
    def test_get_database_config_not_configured(self):
        """Test error when database not configured."""
        from wbweb.core.database.config import get_database_config
        
        with pytest.raises(RuntimeError, match="No database configuration set"):
            get_database_config()


class TestEngineCreation:
    """Test database engine creation."""
    
    def setup_method(self):
        """Reset configuration before each test."""
        import wbweb.core.database.config
        # Reset global state
        wbweb.core.database.config._database_config = None
        wbweb.core.database.config._engine = None
        wbweb.core.database.config._session_maker = None
    
    def test_get_engine_not_configured(self):
        """Test error when getting engine without configuration."""
        from wbweb.core.database.config import get_engine
        
        with pytest.raises(RuntimeError, match="No database configuration set"):
            get_engine()


class TestSessionMakerCreation:
    """Test async session maker creation."""
    
    def setup_method(self):
        """Reset configuration before each test."""
        import wbweb.core.database.config
        # Reset global state
        wbweb.core.database.config._database_config = None
        wbweb.core.database.config._engine = None
        wbweb.core.database.config._session_maker = None
    
    @patch('wbweb.core.database.config.async_sessionmaker')
    @patch('wbweb.core.database.config.get_engine')
    def test_get_async_session_maker(self, mock_get_engine, mock_async_sessionmaker):
        """Test async session maker creation."""
        from wbweb.core.database.config import get_async_session_maker
        from sqlalchemy.ext.asyncio import AsyncSession
        
        mock_engine = Mock(spec=AsyncEngine)
        mock_get_engine.return_value = mock_engine
        mock_session_maker = Mock(spec=async_sessionmaker)
        mock_async_sessionmaker.return_value = mock_session_maker
        
        session_maker = get_async_session_maker()
        
        # Verify async_sessionmaker was called correctly
        mock_async_sessionmaker.assert_called_once_with(
            mock_engine, class_=AsyncSession, expire_on_commit=False
        )
        assert session_maker is mock_session_maker
    
    @patch('wbweb.core.database.config.async_sessionmaker')
    @patch('wbweb.core.database.config.get_engine')
    def test_get_async_session_maker_caching(self, mock_get_engine, mock_async_sessionmaker):
        """Test that session maker is cached and reused."""
        from wbweb.core.database.config import get_async_session_maker
        
        mock_engine = Mock(spec=AsyncEngine)
        mock_get_engine.return_value = mock_engine
        mock_session_maker = Mock(spec=async_sessionmaker)
        mock_async_sessionmaker.return_value = mock_session_maker
        
        # Call get_async_session_maker multiple times
        session_maker1 = get_async_session_maker()
        session_maker2 = get_async_session_maker()
        
        # Should only create session maker once
        assert mock_async_sessionmaker.call_count == 1
        assert session_maker1 is session_maker2 is mock_session_maker


class TestDatabaseUtilities:
    """Test database utility functions."""
    
    def setup_method(self):
        """Reset configuration before each test."""
        import wbweb.core.database.config
        # Reset global state
        wbweb.core.database.config._database_config = None
        wbweb.core.database.config._engine = None
        wbweb.core.database.config._session_maker = None
    
    @pytest.mark.asyncio
    @patch('wbweb.core.database.config.get_engine')
    async def test_create_tables(self, mock_get_engine):
        """Test create_tables function."""
        from wbweb.core.database.config import create_tables
        
        # Mock engine and connection
        mock_conn = AsyncMock()
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = mock_conn
        mock_context_manager.__aexit__.return_value = None
        
        mock_engine = Mock()
        mock_engine.begin.return_value = mock_context_manager
        mock_get_engine.return_value = mock_engine
        
        await create_tables()
        
        # Verify engine.begin() was called and run_sync was called
        mock_engine.begin.assert_called_once()
        mock_conn.run_sync.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('wbweb.core.database.config.get_engine')
    async def test_drop_tables(self, mock_get_engine):
        """Test drop_tables function."""
        from wbweb.core.database.config import drop_tables
        
        # Mock engine and connection
        mock_conn = AsyncMock()
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = mock_conn
        mock_context_manager.__aexit__.return_value = None
        
        mock_engine = Mock()
        mock_engine.begin.return_value = mock_context_manager
        mock_get_engine.return_value = mock_engine
        
        await drop_tables()
        
        # Verify engine.begin() was called and run_sync was called
        mock_engine.begin.assert_called_once()
        mock_conn.run_sync.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('wbweb.core.database.config.get_async_session_maker')
    async def test_get_db_session(self, mock_get_session_maker):
        """Test get_db_session function."""
        from wbweb.core.database.config import get_db_session
        
        # Mock session maker and session
        mock_session = AsyncMock()
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = mock_session
        mock_context_manager.__aexit__.return_value = None
        
        mock_session_maker = Mock()
        mock_session_maker.return_value = mock_context_manager
        mock_get_session_maker.return_value = mock_session_maker
        
        # Use async generator
        async_gen = get_db_session()
        session = await async_gen.__anext__()
        
        # Verify session maker was called
        mock_get_session_maker.assert_called_once()
        mock_session_maker.assert_called_once()
        assert session is mock_session


class TestManagerIntegration:
    """Test integration with Manager system."""
    
    def setup_method(self):
        """Reset configuration before each test."""
        import wbweb.core.database.config
        # Reset global state
        wbweb.core.database.config._database_config = None
        wbweb.core.database.config._engine = None
        wbweb.core.database.config._session_maker = None
    
    @patch('wbweb.core.database.config.get_async_session_maker')
    def test_get_session_for_managers(self, mock_get_session_maker):
        """Test getting session maker for Manager configuration."""
        from wbweb.core.database.config import get_session_for_managers
        
        mock_session_maker = Mock()
        mock_get_session_maker.return_value = mock_session_maker
        
        result = get_session_for_managers()
        
        mock_get_session_maker.assert_called_once()
        assert result is mock_session_maker