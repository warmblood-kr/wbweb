"""
Pytest configuration and fixtures for wbweb tests.
"""

import pytest
import os


@pytest.fixture
def environ():
    """
    Provide clean environment variable management for tests.
    
    Returns a dict-like object that tests can modify, and changes
    are automatically cleaned up after each test. The settings object
    will automatically detect environment changes and reload.
    
    Usage:
        def test_something(environ):
            environ['WBWEB_SETTINGS_MODULE'] = 'tests.test_settings_partial_override'
            from wbweb.core.config import settings
            assert settings.DEBUG is True  # Automatically reloaded
    """
    original_environ = os.environ.copy()
    
    yield os.environ
    
    # Cleanup: restore original environment
    os.environ.clear()
    os.environ.update(original_environ)