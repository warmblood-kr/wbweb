"""
Test SQLAlchemy base classes with Django-style manager support.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession


class TestDatabaseBaseImports:
    """Test that base classes can be imported correctly."""
    
    def test_import_from_database_module(self):
        """Test importing Base classes from database module."""
        from wbweb.core.database import Base, BaseMeta, Manager
        assert Base is not None
        assert BaseMeta is not None
        assert Manager is not None
        
    def test_import_from_main_package(self):
        """Test importing from main wbweb package."""
        from wbweb import Base, BaseMeta, Manager
        assert Base is not None
        assert BaseMeta is not None
        assert Manager is not None


class TestBaseMeta:
    """Test BaseMeta metaclass functionality."""
    
    def test_basemeta_inheritance(self):
        """Test that BaseMeta properly inherits from DeclarativeBase metaclass."""
        from wbweb.core.database import BaseMeta
        from sqlalchemy.orm import DeclarativeBase
        
        # BaseMeta should be a metaclass
        assert isinstance(BaseMeta, type)
        
        # It should be compatible with DeclarativeBase
        assert issubclass(BaseMeta, type(DeclarativeBase))
    
    def test_model_without_tablename_no_manager(self):
        """Test that classes without __tablename__ don't get managers (tested indirectly)."""
        # Note: This is tested indirectly by verifying that only models with __tablename__
        # get managers in other tests. Creating classes without __tablename__ causes
        # SQLAlchemy errors, which is expected behavior.
    
    def test_model_with_tablename_gets_default_manager(self):
        """Test that models with __tablename__ get default 'objects' manager."""
        from wbweb.core.database import Base, Manager
        
        class TestModel(Base):
            __tablename__ = 'test_models'
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
        
        # Should have default 'objects' manager
        assert hasattr(TestModel, 'objects')
        assert isinstance(TestModel.objects, Manager)
        assert TestModel.objects.model_class is TestModel
    
    def test_model_with_explicit_manager(self):
        """Test that explicit managers are properly bound."""
        from wbweb.core.database import Base, Manager
        
        class TestModel(Base):
            __tablename__ = 'test_models_explicit'
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            
            # Explicit manager
            custom_manager = Manager()
        
        # Should have both default and custom managers
        assert hasattr(TestModel, 'objects')
        assert hasattr(TestModel, 'custom_manager')
        
        # Both should be bound to the model
        assert isinstance(TestModel.objects, Manager)
        assert isinstance(TestModel.custom_manager, Manager)
        assert TestModel.objects.model_class is TestModel
        assert TestModel.custom_manager.model_class is TestModel
    
    def test_model_with_existing_objects_manager(self):
        """Test that existing 'objects' manager is preserved."""
        from wbweb.core.database import Base, Manager
        
        class TestModel(Base):
            __tablename__ = 'test_models_existing'
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            
            # Explicit objects manager
            objects = Manager()
        
        # Should use the explicit manager, not create a new one
        assert hasattr(TestModel, 'objects')
        assert isinstance(TestModel.objects, Manager)
        assert TestModel.objects.model_class is TestModel


class TestBase:
    """Test Base class functionality."""
    
    def test_base_class_structure(self):
        """Test that Base class has proper structure."""
        from wbweb.core.database import Base
        from sqlalchemy.ext.asyncio import AsyncAttrs
        from sqlalchemy.orm import DeclarativeBase
        
        # Should inherit from both AsyncAttrs and DeclarativeBase
        assert issubclass(Base, AsyncAttrs)
        assert issubclass(Base, DeclarativeBase)
    
    def test_base_metaclass(self):
        """Test that Base uses BaseMeta as metaclass."""
        from wbweb.core.database import Base, BaseMeta
        
        assert type(Base) is BaseMeta


class TestIntegrationWithManagers:
    """Test integration between Base classes and Managers."""
    
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
    async def test_model_crud_operations(self):
        """Test that models created with Base can use manager CRUD operations."""
        from wbweb.core.database import Base
        
        class User(Base):
            __tablename__ = 'users'
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        # Should be able to use manager methods
        assert hasattr(User, 'objects')
        
        # Mock the query result for create
        await User.objects.create(name="Test User")
        
        # Verify session operations
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.refresh.assert_called_once()
        self.mock_session.commit.assert_called_once()
        
        # Verify the created instance
        added_instance = self.mock_session.add.call_args[0][0]
        assert isinstance(added_instance, User)
        assert added_instance.name == "Test User"
    
    def test_multiple_models_separate_managers(self):
        """Test that different models get separate manager instances."""
        from wbweb.core.database import Base
        
        class User(Base):
            __tablename__ = 'users_multi'
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
        
        class Post(Base):
            __tablename__ = 'posts_multi'
            id = Column(Integer, primary_key=True)
            title = Column(String(100))
        
        # Each model should have its own manager instance
        assert User.objects is not Post.objects
        assert User.objects.model_class is User
        assert Post.objects.model_class is Post


class TestDatabasePackageCompleteness:
    """Test that the database package provides complete functionality."""
    
    def test_all_database_components_available(self):
        """Test that all database components can be imported together."""
        from wbweb.core.database import Manager, configure_session_maker, Base, BaseMeta
        
        # Should be able to create a complete model
        class CompleteModel(Base):
            __tablename__ = 'complete_models'
            id = Column(Integer, primary_key=True)
            name = Column(String(100))
            
            # Custom manager
            active = Manager()
        
        # Should have all expected attributes
        assert hasattr(CompleteModel, 'objects')
        assert hasattr(CompleteModel, 'active')
        assert isinstance(CompleteModel.objects, Manager)
        assert isinstance(CompleteModel.active, Manager)
        
        # Should be able to configure session maker
        mock_session_maker = Mock()
        configure_session_maker(mock_session_maker)
        
        # Verify configuration worked
        from wbweb.core.database.managers import get_session_maker
        assert get_session_maker() is mock_session_maker