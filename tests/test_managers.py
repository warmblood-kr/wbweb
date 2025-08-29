"""
Test Django-style managers with actual database operations.
"""

import pytest
import pytest_asyncio
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, joinedload, relationship
from wbweb import Base, Manager
from wbweb.core.database.managers import AsyncQuerySet


class ProfileModel(Base):
    """Test profile model for relationship testing."""
    __tablename__ = 'test_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('test_users.id'))
    bio = Column(String(200))


class UserModel(Base):
    """Test model for manager operations."""
    __tablename__ = 'test_users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    
    # Add relationship for testing joinedload
    profile = relationship("ProfileModel", back_populates="user")


# Add back_populates
ProfileModel.user = relationship("UserModel", back_populates="profile")


class TestAsyncQuerySetWithDatabase:
    """Test AsyncQuerySet with actual SQLite database."""
    
    @pytest_asyncio.fixture
    async def setup_database(self):
        """Set up in-memory SQLite database with test data."""
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        from wbweb.core.database.managers import get_session
        
        # Create in-memory SQLite database
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Mock get_session to use our test database
        session_maker = async_sessionmaker(engine, expire_on_commit=False)
        
        # Override get_session for tests
        import wbweb.core.database.managers as managers_module
        original_get_session = managers_module.get_session
        async def test_get_session():
            return session_maker()
        managers_module.get_session = test_get_session
        
        # Add test data
        async with session_maker() as session:
            users = [
                UserModel(name='Alice', email='alice@test.com'),
                UserModel(name='Bob', email='bob@test.com'),
                UserModel(name='Charlie', email='charlie@test.com'),
            ]
            session.add_all(users)
            await session.commit()
        
        yield engine
        
        # Cleanup
        managers_module.get_session = original_get_session
        await engine.dispose()
    
    @pytest.mark.asyncio
    async def test_double_filter_chaining(self, setup_database):
        """Test .filter().filter() adds WHERE conditions correctly."""
        UserModel.objects = Manager(UserModel)
        
        # This should work with actual database
        result = await UserModel.objects.filter(name='Alice').filter(email='alice@test.com')
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].name == 'Alice'
    
    @pytest.mark.asyncio
    async def test_queryset_iteration(self, setup_database):
        """Test async iteration over QuerySet."""
        UserModel.objects = Manager(UserModel)
        
        names = []
        async for user in UserModel.objects.all():
            names.append(user.name)
        
        assert len(names) == 3
        assert 'Alice' in names
        assert 'Bob' in names
        assert 'Charlie' in names
    
    @pytest.mark.asyncio  
    async def test_await_then_iterate(self, setup_database):
        """Test await QuerySet then use as list."""
        UserModel.objects = Manager(UserModel)
        
        users = await UserModel.objects.all()
        
        # Should behave like list
        assert isinstance(users, list)
        assert len(users) == 3
        
        # List comprehension should work
        names = [user.name for user in users]
        assert len(names) == 3
    
    @pytest.mark.asyncio
    async def test_options_generates_join(self, setup_database):
        """Test that .options() with joinedload() generates JOIN in SQL."""
        UserModel.objects = Manager(UserModel)
        
        # Create QuerySet with joinedload
        qs = UserModel.objects.filter(name='Alice').options(
            joinedload(UserModel.profile)
        )
        
        # Check that it's still AsyncQuerySet
        assert isinstance(qs, AsyncQuerySet)
        
        # The SQL should contain both WHERE (from filter) and JOIN (from options)
        stmt_str = str(qs._stmt)
        assert 'name' in stmt_str
        assert 'WHERE' in stmt_str
        assert 'JOIN' in stmt_str  # This verifies options() actually works
    
    @pytest.mark.asyncio
    async def test_order_by_ascending(self, setup_database):
        """Test order_by with ascending order (default)."""
        UserModel.objects = Manager(UserModel)
        
        users = await UserModel.objects.order_by(UserModel.name)
        names = [user.name for user in users]
        
        assert names == ['Alice', 'Bob', 'Charlie']
    
    @pytest.mark.asyncio
    async def test_order_by_descending(self, setup_database):
        """Test order_by with descending order."""
        UserModel.objects = Manager(UserModel)
        
        users = await UserModel.objects.order_by(UserModel.name.desc())
        names = [user.name for user in users]
        
        assert names == ['Charlie', 'Bob', 'Alice']
    
    @pytest.mark.asyncio
    async def test_order_by_chaining_replaces(self, setup_database):
        """Test that multiple order_by calls replace previous ordering."""
        UserModel.objects = Manager(UserModel)
        
        # First order by name, then by email - should only order by email
        users = await UserModel.objects.order_by(UserModel.name).order_by(UserModel.email)
        emails = [user.email for user in users]
        
        # Should be ordered by email, not name
        assert emails == ['alice@test.com', 'bob@test.com', 'charlie@test.com']
    
    @pytest.mark.asyncio
    async def test_order_by_with_filter_chaining(self, setup_database):
        """Test chaining order_by with filter."""
        UserModel.objects = Manager(UserModel)
        
        # Filter then order
        users = await UserModel.objects.filter(name='Alice').order_by(UserModel.email)
        assert len(users) == 1
        assert users[0].name == 'Alice'
        
        # Order then filter
        users = await UserModel.objects.order_by(UserModel.name.desc()).filter(name='Bob')
        assert len(users) == 1
        assert users[0].name == 'Bob'
