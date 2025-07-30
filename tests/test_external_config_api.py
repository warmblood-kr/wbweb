"""
Test the external wbweb.config API for external projects

This test validates that external projects (like monocle-stark) can use the clean
import pattern: from wbweb.config import settings
"""


class TestExternalConfigAPI:
    """Test the external config API import patterns"""
    
    def test_external_import_works(self):
        """Test that 'from wbweb.config import settings' works with expected defaults"""
        
        from wbweb.config import settings
        
        assert settings.DATABASE_ENGINE_FACTORY == 'wbweb.core.database.engine_factory.DefaultEngineFactory'
    
    def test_external_and_internal_imports_same_object(self):
        """Test that external and internal imports reference the same settings object"""
        
        from wbweb.config import settings as external_settings
        from wbweb.core.config import settings as internal_settings
        
        assert external_settings is internal_settings