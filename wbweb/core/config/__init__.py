"""
Django-style configuration system for wbweb.

Provides centralized settings management with support for child project overrides.

Usage:
    # Universal import across wbweb ecosystem
    from wbweb.core.config import settings
    
    # Child projects can override via environment variable
    # WBWEB_SETTINGS_MODULE='myproject.settings'
"""

from .settings import settings

__all__ = ['settings']