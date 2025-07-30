"""
Engine Factory for SQLAlchemy

Provides configurable database engine factories with support for:
- Standard SQLAlchemy engines
- AWS RDS IAM authentication
- AWS SecretManager integration
- Runtime backend switching via environment variables
"""

import json
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine
from ..utils.proxy import ConfigurableBackendProxy


def is_async_url(url: str) -> bool:
    """Detect if database URL uses async driver"""
    if not url:
        return False
    async_drivers = ['aiosqlite', 'asyncpg', 'aiomysql', 'asyncio']
    return any(driver in url for driver in async_drivers)


class DefaultEngineFactory:
    """Default engine factory with connection caching"""

    def __init__(self):
        self._engines = {}

    def create_engine(self, database_url):
        """Create or return cached engine - reuses connection pools"""
        if database_url in self._engines:
            return self._engines[database_url]
        
        # Choose function based on URL, apply same kwargs
        engine_func = create_async_engine if is_async_url(database_url) else sa.create_engine
        self._engines[database_url] = engine_func(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )
        return self._engines[database_url]


class RdsIamEngineFactory:
    """RDS IAM engine factory with connection caching"""

    def __init__(self):
        self._engines = {}

    def create_engine(self, database_url):
        """Create or return cached RDS IAM engine"""
        if database_url in self._engines:
            return self._engines[database_url]
        
        import boto3
        engine_url = sa.engine.url.make_url(database_url)
        
        # Choose function based on URL, apply same kwargs
        engine_func = create_async_engine if is_async_url(database_url) else sa.create_engine
        engine = engine_func(
            f'{engine_url.drivername}:///',
            pool_size=10,
            max_overflow=20,
            pool_recycle=900,   # TODO: Issue #12 - Verify IAM token vs connection lifecycle
            pool_pre_ping=True
        )

        @sa.event.listens_for(engine.sync_engine if hasattr(engine, 'sync_engine') else engine, 'do_connect')
        def provide_token(dialect, conn_rec, cargs, cparams):
            client = boto3.client('rds')
            token = client.generate_db_auth_token(
                DBHostname=engine_url.host,
                Port=engine_url.port,
                DBUsername=engine_url.username,
                Region=engine_url.query.get('region', 'us-east-1')
            )
            if engine_url.host:
                cparams['host'] = engine_url.host
            if engine_url.port:
                cparams['port'] = engine_url.port
            if engine_url.username:
                cparams['user'] = engine_url.username
            cparams['password'] = token
            if engine_url.database:
                cparams['database'] = engine_url.database
        
        self._engines[database_url] = engine
        return engine


class SecretManagerEngineFactory:
    """AWS SecretManager engine factory with connection caching"""

    def __init__(self):
        self._engines = {}

    def create_engine(self, database_url):
        """Create or return cached SecretManager engine"""
        if database_url in self._engines:
            return self._engines[database_url]
        
        import boto3
        engine_url = sa.engine.url.make_url(database_url)
        secret_arn = engine_url.query.get('secret_arn')

        secrets_client = boto3.client('secretsmanager')
        secret_response = secrets_client.get_secret_value(SecretId=secret_arn)
        secret_dict = json.loads(secret_response['SecretString'])

        # Create clean URL with just the database connection info (no query parameters)
        clean_url = sa.engine.url.URL.create(
            drivername=engine_url.drivername,
            username=engine_url.username,
            password=secret_dict['password'],
            host=engine_url.host,
            port=engine_url.port,
            database=engine_url.database
        )
        
        # Choose function based on URL, apply same kwargs
        engine_func = create_async_engine if is_async_url(str(clean_url)) else sa.create_engine
        engine = engine_func(
            clean_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )
        
        self._engines[database_url] = engine
        return engine


# Global configurable engine factory instance
engine_factory = ConfigurableBackendProxy(
    'DATABASE_ENGINE_FACTORY',
    'wbweb.core.database.engine_factory.DefaultEngineFactory'
)