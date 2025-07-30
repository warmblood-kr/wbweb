"""
Tests for database configuration system.

NOTE: Most database configuration functions have been removed since 
stark (our primary user) doesn't use them. stark uses engine_factory directly.

This test file is kept minimal to verify the cleaned up state.
"""

class TestDatabaseConfigCleanup:
    """Test that old database config functions have been properly removed"""
    
    def test_old_functions_removed_from_module(self):
        """Test that removed functions are no longer importable from database module"""
        import wbweb.core.database
        
        # These functions should NOT exist anymore
        removed_functions = [
            'configure_database', 'get_engine', 'get_async_session_maker',
            'create_tables', 'drop_tables', 'get_db_session', 'get_session_for_managers'
        ]
        
        for func_name in removed_functions:
            assert not hasattr(wbweb.core.database, func_name), f"{func_name} should be removed"
    
    def test_old_functions_removed_from_main_package(self):
        """Test that removed functions are not in main wbweb package"""
        import wbweb
        
        # These functions should NOT exist in main package either
        removed_functions = [
            'configure_database', 'get_engine', 'get_async_session_maker',
            'create_tables', 'drop_tables', 'get_db_session'
        ]
        
        for func_name in removed_functions:
            assert not hasattr(wbweb, func_name), f"{func_name} should be removed from main package"
    
    def test_essential_functions_still_exist(self):
        """Test that functions stark actually uses still exist"""
        from wbweb import Manager, Base, BaseMeta
        from wbweb.core.database import configure_session_maker
        
        # These should still exist (used by stark)
        assert Manager is not None
        assert Base is not None  
        assert BaseMeta is not None
        assert configure_session_maker is not None