"""
Generic backend proxy utilities for configuration-based backend systems.

Provides Django-style proxies that allow runtime configuration changes
to take effect without requiring module reloads - essential for testing.
"""

import importlib


def import_from_string(classpath):
    """Import a class from a module path string."""
    module_path, class_name = classpath.rsplit('.', 1)
    module = importlib.import_module(module_path)
    backend_class = getattr(module, class_name)
    return backend_class


class ConfigurableBackendProxy:
    """
    Generic proxy for backends that resolves the actual backend dynamically
    based on Django-style settings. Allows config changes (like in tests) to take 
    effect without requiring module reload.
    
    Usage:
        # In your module:
        backend = ConfigurableBackendProxy('EMAIL_BACKEND')
        
        # Use normally:
        await backend.send(message, recipients)
        
        # Configuration via Django-style settings:
        # 1. Environment: WBWEB_SETTINGS_MODULE='myproject.settings'
        # 2. Settings: EMAIL_BACKEND = 'my.custom.Backend'
        # 3. Proxy automatically detects changes and recreates backend
    """
    def __init__(self, config_key, default_value=None):
        self.default_value = default_value
        self._config_key = config_key
        self._backend = None
        self._cached_backend_path = None
    
    def _should_recreate_backend(self):
        """Check if backend needs to be recreated due to config change"""
        from ..config import settings
        current_backend_path = getattr(settings, self._config_key, self.default_value)
        is_backend_path_changed = self._cached_backend_path != current_backend_path
        
        return (self._backend is None or is_backend_path_changed)
    
    def _get_or_create_backend(self):
        """Get cached backend or create new one if config changed"""
        if self._should_recreate_backend():
            from ..config import settings
            current_backend_path = getattr(settings, self._config_key, self.default_value)
            backend_class = import_from_string(current_backend_path)
            self._backend = backend_class()
            self._cached_backend_path = current_backend_path
        return self._backend
    
    def __getattr__(self, name):
        backend = self._get_or_create_backend()
        return getattr(backend, name)