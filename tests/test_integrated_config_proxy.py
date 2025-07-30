"""
Integration tests for Django-style config + ConfigurableBackendProxy.

Tests the complete layered architecture:
Environment Variables → Django-style Settings → ConfigurableBackendProxy
"""

import pytest


class TestIntegratedConfigProxy:
    """Test the complete config → proxy integration."""
    
    def test_proxy_uses_settings_for_backend_selection(self, environ):
        """ConfigurableBackendProxy uses Django-style settings."""
        from wbweb.core.utils.proxy import ConfigurableBackendProxy
        
        # Create proxy for DATABASE_ENGINE_FACTORY
        proxy = ConfigurableBackendProxy(
            'DATABASE_ENGINE_FACTORY',
            'wbweb.core.database.engine_factory.DefaultEngineFactory'
        )
        
        # Should use default from settings
        backend = proxy._get_or_create_backend()
        assert backend.__class__.__name__ == 'DefaultEngineFactory'
    
    def test_proxy_responds_to_settings_changes(self, environ):
        """Proxy automatically updates when settings change."""
        from wbweb.core.utils.proxy import ConfigurableBackendProxy
        
        proxy = ConfigurableBackendProxy(
            'DATABASE_ENGINE_FACTORY',
            'wbweb.core.database.engine_factory.DefaultEngineFactory'
        )
        
        # Start with default
        backend1 = proxy._get_or_create_backend()
        assert backend1.__class__.__name__ == 'DefaultEngineFactory'
        
        # Change settings via child project override
        environ['WBWEB_SETTINGS_MODULE'] = 'tests.test_settings_proxy_override'
        
        # Should automatically detect change and recreate
        backend2 = proxy._get_or_create_backend()
        assert backend2.__class__.__name__ == 'RdsIamEngineFactory'
        assert backend2 is not backend1  # New instance created
    
    def test_layered_fallback_architecture(self, environ):
        """Test Environment → Settings → Proxy → Default fallback chain."""
        from wbweb.core.utils.proxy import ConfigurableBackendProxy
        
        proxy = ConfigurableBackendProxy(
            'CUSTOM_ENGINE_FACTORY',  # Not in any settings
            'wbweb.core.database.engine_factory.DefaultEngineFactory'  # Proxy default
        )
        
        # Should fallback all the way to proxy default
        backend = proxy._get_or_create_backend()
        assert backend.__class__.__name__ == 'DefaultEngineFactory'
    
    def test_engine_factory_global_instance_works(self, environ):
        """The global engine_factory instance works with settings."""
        from wbweb.core.database.engine_factory import engine_factory
        
        # Should work with default settings
        engine = engine_factory.create_engine('sqlite+aiosqlite:///test.db')
        assert hasattr(engine, 'begin')  # Async engine
        
        # Should respond to settings changes
        environ['WBWEB_SETTINGS_MODULE'] = 'tests.test_settings_proxy_override'
        
        # Force backend recreation by accessing after settings change
        new_backend = engine_factory._get_or_create_backend()
        assert new_backend.__class__.__name__ == 'RdsIamEngineFactory'