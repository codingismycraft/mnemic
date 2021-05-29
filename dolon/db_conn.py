"""Wraps db connection pool within a context manager."""

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

    def __init__(self, min_size=1, max_size=10, conn_str=None):
        """Initializer.

        :param int min_size: The min number of pooled connections.
        :param int max_size: The max number of pooled connections.
        :param str|None conn_str: The connection string to the db.
        """
        self._min_size = min_size
        self._max_size = max_size
        self._conn_str = conn_str

    async def __aenter__(self):
        """Enters the context."""
        self._impl = db_conn_impl.DbConnectionImpl(
            min_size=self._min_size,
            max_size=self._max_size,
            conn_str=self._conn_str
        )
        return await self._impl.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exits from the context."""
        if self._impl:
            await self._impl.__aexit__(exc_type, exc_val, exc_tb)
            self._impl = None
