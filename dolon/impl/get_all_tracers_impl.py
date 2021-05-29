import dolon.impl.constants as constants
import dolon.db_conn as db_conn

# Aliases.
DbConnection = db_conn.DbConnection

_PREFETCH_SIZE = 100


async def get_all_tracers():
    tracers = []
    async with DbConnection() as db:
        tracer_names = await _get_tracer_names(db)
        for tracer_name in tracer_names:
            tracers.append(
                {
                    "tracer_name": tracer_name,
                    'runs': await _get_tracer_runs(db, tracer_name)
                }
            )

        return tracers


async def _get_tracer_names(db):
    tracer_names = []
    conn_pool = db.get_conn_pool()
    async with conn_pool.acquire() as conn:
        stmt = await conn.prepare(constants.SQL_SELECT_ALL_TRACER_RUNS)
        async with conn.transaction():
            async for record in stmt.cursor(prefetch=_PREFETCH_SIZE):
                tracer_names.append(record['app_name'])
    return tracer_names


async def _get_tracer_runs(db, app_name):
    tracer_runs = []
    conn_pool = db.get_conn_pool()
    async with conn_pool.acquire() as conn:
        stmt = await conn.prepare(constants.SQL_SELECT_RUNS)
        async with conn.transaction():
            async for record in stmt.cursor(app_name, prefetch=_PREFETCH_SIZE):
                tracer_runs.append(
                    {
                        'creation_time': record['creation_time'],
                        'uuid': record['uuid'],
                    }

                )
    return tracer_runs
