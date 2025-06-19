"""
Test Django-style managers extraction and functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String


class MockBase(DeclarativeBase):
    """Mock base class for testing."""
    pass


class MockModel(MockBase):
    """Mock model for testing managers."""
    __tablename__ = 'test_model'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestManagerImports:
    """Test that managers can be imported correctly."""
    
    def test_import_from_database_module(self):
        """Test importing Manager from database module."""
        from wbweb.core.database import Manager
        assert Manager is not None
        
    def test_import_from_main_package(self):
        """Test importing from main wbweb package."""
        from wbweb import Manager
        assert Manager is not None


class TestManagerConfiguration:
    """Test manager configuration system."""
    
    def test_configure_session_maker(self):
        """Test configuring session maker."""
        from wbweb.core.database.managers import configure_session_maker, get_session_maker
        
        mock_session_maker = Mock()
        configure_session_maker(mock_session_maker)
        
        result = get_session_maker()
        assert result is mock_session_maker
        
    def test_get_session_maker_not_configured(self):
        """Test error when session maker not configured."""
        from wbweb.core.database.managers import get_session_maker, _session_maker
        
        # Reset global state
        import wbweb.core.database.managers
        wbweb.core.database.managers._session_maker = None
        
        with pytest.raises(RuntimeError, match="No session maker configured"):
            get_session_maker()


class TestManagerBasicFunctionality:
    """Test basic manager functionality."""
    
    def test_manager_initialization(self):
        """Test manager can be initialized with model class."""
        from wbweb.core.database import Manager
        
        manager = Manager(MockModel)
        assert manager.model_class is MockModel
        assert manager._session is None
        
    def test_manager_initialization_without_model(self):
        """Test manager can be initialized without model class."""
        from wbweb.core.database import Manager
        
        manager = Manager()
        assert manager.model_class is None
        assert manager._session is None


class TestManagerCRUDOperations:
    """Test manager CRUD operations with mocked sessions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        from wbweb.core.database.managers import configure_session_maker
        
        # Create mock session and session maker
        self.mock_session = AsyncMock(spec=AsyncSession)
        
        # Create async context manager mock
        self.mock_context_manager = AsyncMock()
        self.mock_context_manager.__aenter__.return_value = self.mock_session
        self.mock_context_manager.__aexit__.return_value = None
        
        self.mock_session_maker = Mock()
        self.mock_session_maker.return_value = self.mock_context_manager
        
        # Configure the session maker
        configure_session_maker(self.mock_session_maker)
    
    @pytest.mark.asyncio
    async def test_create_operation(self):
        """Test creating a new model instance."""
        from wbweb.core.database import Manager
        
        manager = Manager(MockModel)
        
        # Create instance
        result = await manager.create(name="Test Item")
        
        # Verify session operations
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.refresh.assert_called_once()
        self.mock_session.commit.assert_called_once()
        
        # Verify the created instance
        added_instance = self.mock_session.add.call_args[0][0]
        assert isinstance(added_instance, MockModel)
        assert added_instance.name == "Test Item"
    
    @pytest.mark.asyncio
    async def test_get_operation(self):
        """Test getting a single model instance."""
        from wbweb.core.database import Manager
        
        manager = Manager(MockModel)
        
        # Mock the query result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = MockModel(id=1, name="Found Item")
        self.mock_session.execute.return_value = mock_result
        
        # Get instance
        result = await manager.get(name="Found Item")
        
        # Verify session operations
        self.mock_session.execute.assert_called_once()
        self.mock_session.commit.assert_called_once()
        
        # Verify result
        assert result.name == "Found Item"
        assert result.id == 1
    
    @pytest.mark.asyncio
    async def test_filter_operation(self):
        """Test filtering model instances."""
        from wbweb.core.database import Manager
        
        manager = Manager(MockModel)
        
        # Mock the query result
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = [
            MockModel(id=1, name="Item 1"),
            MockModel(id=2, name="Item 2")
        ]
        mock_result.scalars.return_value = mock_scalars
        self.mock_session.execute.return_value = mock_result
        
        # Filter instances
        result = await manager.filter(name="Test")
        
        # Verify session operations
        self.mock_session.execute.assert_called_once()
        self.mock_session.commit.assert_called_once()
        
        # Verify result
        assert len(result) == 2
        assert result[0].name == "Item 1"
        assert result[1].name == "Item 2"
    
    @pytest.mark.asyncio
    async def test_all_operation(self):
        """Test getting all model instances."""
        from wbweb.core.database import Manager
        
        manager = Manager(MockModel)
        
        # Mock the query result
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = [
            MockModel(id=1, name="Item 1"),
            MockModel(id=2, name="Item 2"),
            MockModel(id=3, name="Item 3")
        ]
        mock_result.scalars.return_value = mock_scalars
        self.mock_session.execute.return_value = mock_result
        
        # Get all instances
        result = await manager.all()
        
        # Verify session operations
        self.mock_session.execute.assert_called_once()
        self.mock_session.commit.assert_called_once()
        
        # Verify result
        assert len(result) == 3
        assert all(isinstance(item, MockModel) for item in result)
    
    @pytest.mark.asyncio
    async def test_get_or_create_existing(self):
        """Test get_or_create when instance exists."""
        from wbweb.core.database import Manager
        
        manager = Manager(MockModel)
        
        # Mock existing instance
        existing_instance = MockModel(id=1, name="Existing Item")
        
        # Mock get method to return existing instance
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = existing_instance
        self.mock_session.execute.return_value = mock_result
        
        # Get or create
        result, created = await manager.get_or_create(name="Existing Item")
        
        # Verify result
        assert result is existing_instance
        assert created is False
        assert not self.mock_session.add.called  # Should not create new instance
    
    @pytest.mark.asyncio
    async def test_get_or_create_new(self):
        """Test get_or_create when instance doesn't exist."""
        from wbweb.core.database import Manager
        
        manager = Manager(MockModel)
        
        # Mock get method to return None (not found)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_session.execute.return_value = mock_result
        
        # Get or create
        result, created = await manager.get_or_create(
            defaults={"name": "New Item"}, 
            id=1
        )
        
        # Verify result
        assert created is True
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.refresh.assert_called_once()


class TestManagerErrorHandling:
    """Test manager error handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        from wbweb.core.database.managers import configure_session_maker
        
        # Create mock session and session maker
        self.mock_session = AsyncMock(spec=AsyncSession)
        
        # Create async context manager mock
        self.mock_context_manager = AsyncMock()
        self.mock_context_manager.__aenter__.return_value = self.mock_session
        self.mock_context_manager.__aexit__.return_value = None
        
        self.mock_session_maker = Mock()
        self.mock_session_maker.return_value = self.mock_context_manager
        
        # Configure the session maker
        configure_session_maker(self.mock_session_maker)
    
    @pytest.mark.asyncio
    async def test_rollback_on_exception(self):
        """Test that session is rolled back on exception."""
        from wbweb.core.database import Manager
        
        manager = Manager(MockModel)
        
        # Make flush raise an exception
        self.mock_session.flush.side_effect = Exception("Database error")
        
        # Create should raise exception and rollback
        with pytest.raises(Exception, match="Database error"):
            await manager.create(name="Test Item")
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
        assert not self.mock_session.commit.called  # Should not commit on error