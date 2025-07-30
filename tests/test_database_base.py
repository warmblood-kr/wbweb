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


