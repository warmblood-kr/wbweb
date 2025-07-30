"""
Regression tests for Django-style config fallback mechanism.

Tests that settings properly fallback to wbweb defaults when child projects
only override some settings. Uses the global settings object that everyone
imports in real usage.
"""

import pytest


class TestConfigFallbackMechanism:
    """Test that settings fallback to defaults when not overridden."""
    
    def test_partial_override_falls_back_to_defaults(self, environ):
        """Child project partial overrides fallback to wbweb defaults."""
        environ['WBWEB_SETTINGS_MODULE'] = 'tests.test_settings_partial_override'
        
        from wbweb.core.config import settings
        
        # Test overridden values work
        assert settings.DEBUG is True  # Overridden in test settings
        assert settings.CUSTOM_SETTING == 'from_test_child_project'  # New setting
        assert settings.APP_NAME == 'Test Fallback Application'  # Overridden
        
        # Test fallback to defaults works
        assert settings.DATABASE_URL == 'sqlite+aiosqlite:///wbweb.db'  # Default
        assert settings.ENVIRONMENT == 'production'  # Default
        assert settings.DATABASE_ENGINE_FACTORY == 'wbweb.core.database.engine_factory.DefaultEngineFactory'  # Default
    
    def test_no_override_uses_all_defaults(self, environ):
        """When no WBWEB_SETTINGS_MODULE, all settings use defaults."""
        # Ensure no WBWEB_SETTINGS_MODULE is set
        environ.pop('WBWEB_SETTINGS_MODULE', None)
        
        from wbweb.core.config import settings
        
        # All should be defaults
        assert settings.DEBUG is False
        assert settings.DATABASE_URL == 'sqlite+aiosqlite:///wbweb.db'
        assert settings.APP_NAME == 'wbweb Application'
        assert settings.ENVIRONMENT == 'production'
    
    def test_nonexistent_setting_raises_error(self):
        """Accessing nonexistent setting raises AttributeError."""
        from wbweb.core.config import settings
        
        with pytest.raises(AttributeError, match="Settings object has no attribute 'NONEXISTENT'"):
            _ = settings.NONEXISTENT
    
    def test_dynamic_reloading_works(self, environ):
        """Settings automatically reload when environment changes."""
        from wbweb.core.config import settings
        
        # Start with defaults
        environ.pop('WBWEB_SETTINGS_MODULE', None)
        assert settings.DEBUG is False  # Default
        
        # Change environment - should automatically reload
        environ['WBWEB_SETTINGS_MODULE'] = 'tests.test_settings_partial_override'
        assert settings.DEBUG is True  # Automatically reloaded!
        
        # Change back - should reload again
        environ.pop('WBWEB_SETTINGS_MODULE', None)
        assert settings.DEBUG is False  # Back to default
    
    def test_invalid_settings_module_raises_import_error(self, environ):
        """Invalid WBWEB_SETTINGS_MODULE raises clear error."""
        environ['WBWEB_SETTINGS_MODULE'] = 'nonexistent.module'
        
        from wbweb.core.config import settings
        
        with pytest.raises(ImportError, match="Could not import settings module"):
            _ = settings.DEBUG