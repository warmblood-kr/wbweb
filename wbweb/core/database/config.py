"""
Database configuration and session management.

This module previously provided global configuration management,
but has been simplified since our primary user (stark) uses 
engine_factory directly rather than global configuration.

For database engines, use:
    from wbweb.core.database.engine_factory import engine_factory
    engine = engine_factory.create_engine(database_url)
"""

# This module is now minimal - global config functions have been removed
# since stark (our primary user) doesn't use them.