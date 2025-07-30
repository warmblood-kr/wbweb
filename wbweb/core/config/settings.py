"""
Django-style central settings object for wbweb.

Provides lazy loading of settings with support for child project overrides
via WBWEB_SETTINGS_MODULE environment variable.
"""

import os
import importlib
from typing import Any


class Settings:
    """
    Central settings object that lazy loads configuration.
    
    Similar to Django's django.conf.settings - this is the single
    source of truth for all configuration across the wbweb ecosystem.
    """
    
    def __init__(self):
        self._settings_module = None
        self._defaults_module = None
        self._cached_settings_module_path = None
    
    def _should_reload_settings(self):
        """Check if settings need to be reloaded due to environment change."""
        current_settings_module_path = os.environ.get('WBWEB_SETTINGS_MODULE')
        is_settings_path_changed = self._cached_settings_module_path != current_settings_module_path
        
        return (self._settings_module is None or is_settings_path_changed)
    
    def _load_settings(self):
        """Load settings from WBWEB_SETTINGS_MODULE or defaults."""
        if not self._should_reload_settings():
            return
            
        # Always load defaults module
        from . import defaults
        self._defaults_module = defaults
        
        # Get settings module from environment
        current_settings_module_path = os.environ.get('WBWEB_SETTINGS_MODULE')
        
        if current_settings_module_path:
            # Load child project settings
            try:
                self._settings_module = importlib.import_module(current_settings_module_path)
            except ImportError as e:
                raise ImportError(
                    f"Could not import settings module '{current_settings_module_path}': {e}"
                ) from e
        else:
            # No override - use defaults as main module
            self._settings_module = defaults
        
        # Cache the current settings module path
        self._cached_settings_module_path = current_settings_module_path
    
    def __getattr__(self, name: str) -> Any:
        """Get setting value with lazy loading and fallback to defaults."""
        self._load_settings()
        
        # Try user settings first (if different from defaults)
        if self._settings_module is not self._defaults_module:
            try:
                return getattr(self._settings_module, name)
            except AttributeError:
                pass
        
        # Fallback to defaults
        try:
            return getattr(self._defaults_module, name)
        except AttributeError:
            raise AttributeError(f"Settings object has no attribute '{name}'")
    
    def __dir__(self):
        """Support for dir() and IDE autocompletion."""
        self._load_settings()
        return dir(self._settings_module)


# Global settings instance - everyone imports this
settings = Settings()