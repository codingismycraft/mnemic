import asyncpg

try:
    import backend.constants as constants
except ModuleNotFoundError:
    import constants


# async def make_conn_pool():
#     return await asyncpg.create_pool(
#         constants.CONN_STR,
#         min_size=1,
#         max_size=10,
#         statement_cache_size=0,
#         max_inactive_connection_lifetime=10,
#         max_queries=1000
#     )


class DbConnection:
    _conn_pool = None

    async def __aenter__(self):
        try:
            print("Trying to connect using: ",  constants.CONN_STR)
            self._conn_pool = await asyncpg.create_pool(
                constants.CONN_STR,
                min_size=1,
                max_size=10,
                statement_cache_size=0,
                max_inactive_connection_lifetime=10,
                max_queries=1000
            )
            print("Connected successfully..")
        except ConnectionRefusedError:
            print("Trying to connect using: ", constants.REMOTE_CONN_STR)
            self._conn_pool = await asyncpg.create_pool(
                constants.REMOTE_CONN_STR,
                min_size=1,
                max_size=10,
                statement_cache_size=0,
                max_inactive_connection_lifetime=10,
                max_queries=1000
            )
            print("Connected successfully..")
        return self._conn_pool

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._conn_pool:
            print("Closing connection")
            await self._conn_pool.close()
            self._conn_pool = None
