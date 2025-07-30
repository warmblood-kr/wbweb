"""
Test settings for proxy integration testing.

Overrides DATABASE_ENGINE_FACTORY to test proxy responds to settings changes.
"""

# Only override what we need - fallback handles the rest
DATABASE_ENGINE_FACTORY = 'wbweb.core.database.engine_factory.RdsIamEngineFactory'