"""Wraps db connection pool within a context manager."""

import dolon.impl.db_conn_impl as db_conn_impl


class DbConnection:
    """Wraps db connection pool within a context manager."""
    _impl = None

    async def __aenter__(self):
        self._impl = db_conn_impl.DbConnectionImpl()
        return await self._impl.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._impl:
            await self._impl.__aexit__(exc_type, exc_val, exc_tb)
            self._impl = None
