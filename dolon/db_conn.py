"""Wraps db connection pool within a context manager."""

import os

import dolon.exceptions as exceptions
import dolon.impl.db_conn_impl as db_conn_impl


class DbConnection:
    """Wraps db connection pool within a context manager.

    :ivar DbConnectionImpl _impl: The implementation object.
    :ivar int _min_size: The min number of pooled connections.
    :ivar int _max_size: The max number of pooled connections.
    :ivar str _conn_str: The connection string to the db.
    """

    _impl = None

    _min_size = None
    _max_size = None
    _conn_str = None

    @classmethod
    def _get_conn_str(cls):
        """Gets the connection string using the environment variables.

        Example of connection string:
        'postgresql://postgres:postgres123@localhost:5432/mnemic'

        :returns: The connection string using the environment variables.
        :rtype: str
        """
        if cls._conn_str:
            return cls._conn_str
        else:
            try:
                return os.environ["POSTGRES_CONN_STR"]
            except KeyError as ex:
                raise exceptions.InvalidEnvironmentVariable(str(ex)) from ex

    def __init__(self, min_size=1, max_size=10):
        """Initializer.

        :param int min_size: The min number of pooled connections.
        :param int max_size: The max number of pooled connections.
        """
        self._min_size = min_size
        self._max_size = max_size

    @classmethod
    def set_conn_str(cls, conn_str):
        """Sets the connection string explicitly.

        The explicitly set connection string will take presidency over the
        corresponding environment value.

        :param str conn_str: The connection string to set.
        """
        cls._conn_str = conn_str

    async def __aenter__(self):
        """Enters the context."""
        self._impl = db_conn_impl.DbConnectionImpl(
            min_size=self._min_size,
            max_size=self._max_size,
            conn_str=self._get_conn_str()
        )
        return await self._impl.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exits from the context."""
        if self._impl:
            await self._impl.__aexit__(exc_type, exc_val, exc_tb)
            self._impl = None
