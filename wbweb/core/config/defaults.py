"""
wbweb framework default settings.

These are the baseline settings that wbweb provides. Child projects can
override these by creating their own settings module and setting
WBWEB_SETTINGS_MODULE environment variable.

Similar to Django's django.conf.global_settings.
"""

# Database Configuration
DATABASE_URL = 'sqlite+aiosqlite:///wbweb.db'
DATABASE_ENGINE_FACTORY = 'wbweb.core.database.engine_factory.DefaultEngineFactory'

# Framework Configuration  
DEBUG = False
ENVIRONMENT = 'production'

# Basic Application Settings
APP_NAME = 'wbweb Application'
APP_DESCRIPTION = 'A wbweb-powered web application'