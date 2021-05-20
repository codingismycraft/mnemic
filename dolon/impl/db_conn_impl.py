"""Wraps db connection pool within a context manager."""

import os

import asyncpg

# Applicable when env variable HOST not set; points to host machine
# when the application lives within a docker container.
_DEFAULT_HOST = "172.17.0.1"


class DbConnectionImpl:
    """Wraps db connection pool within a context manager."""

    _conn_pool = None

    _PREFETCH_SIZE = 100

    def __init__(self, min_size=1, max_size=10, conn_str=None):
        self._min_size = min_size
        self._max_size = max_size
        self._conn_str = conn_str

    def _get_conn_str(self):
        """Returns the database connection string.

        :return: The database connection string.
        :rtype: str
        """
        if self._conn_str:
            return self._conn_str
        else:
            user = os.environ["POSTGRES_USER"]
            password = os.environ["POSTGRES_PASSWORD"]
            db = os.environ["POSTGRES_DB"]
            host = os.environ.get("HOST", _DEFAULT_HOST)

            return f'postgresql://{user}:{password}@{host}:5432/{db}'

    def get_conn_pool(self):
        return self._conn_pool

    async def __aenter__(self):
        self._conn_pool = await asyncpg.create_pool(
            self._get_conn_str(),
            min_size=self._min_size,
            max_size=self._max_size,
            statement_cache_size=0,
            max_inactive_connection_lifetime=10,
            max_queries=1000
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._conn_pool:
            print("Closing connection")
            await self._conn_pool.close()
            self._conn_pool = None

    async def execute_query(self, sql, query_args=None):
        """Executes the passed in sql statement.

        :raises asyncpg.exceptions.PostgresError
        """
        async with self._conn_pool.acquire() as connection:
            statement = await connection.prepare(sql)
            args = query_args or []
            async with connection.transaction():
                async for record in statement.cursor(
                        *args, prefetch=self._PREFETCH_SIZE):
                    yield dict(record)
