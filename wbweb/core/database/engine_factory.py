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
from sqlalchemy.pool import StaticPool
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
        engine_func = create_async_engine if is_async_url(database_url) \
            else sa.create_engine

        # Robust detection of in-memory SQLite without hard-coding driver strings
        url_obj = sa.engine.url.make_url(database_url)

        backend = url_obj.get_backend_name() if hasattr(url_obj, 'get_backend_name') \
            else (url_obj.drivername.split('+', 1)[0] if url_obj.drivername else '')
        database = (url_obj.database or '').strip() if hasattr(url_obj, 'database') \
            else ''

        is_sqlite_memory = True if backend == 'sqlite' and database == ':memory:' \
            else False

        if is_sqlite_memory:
            connect_args = {}

            if engine_func is create_async_engine:
                self._engines[database_url] = create_async_engine(
                    database_url, poolclass=StaticPool, connect_args=connect_args
                )
            else:
                connect_args.setdefault('check_same_thread', False)
                self._engines[database_url] = sa.create_engine(
                    database_url, poolclass=StaticPool, connect_args=connect_args
                )
        else:
            self._engines[database_url] = engine_func(database_url)
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
        engine = engine_func(f'{engine_url.drivername}:///')

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
        engine = engine_func(clean_url)
        
        self._engines[database_url] = engine
        return engine


# Global configurable engine factory instance
engine_factory = ConfigurableBackendProxy(
    'DATABASE_ENGINE_FACTORY',
    'wbweb.core.database.engine_factory.DefaultEngineFactory'
)
