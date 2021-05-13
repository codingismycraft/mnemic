"""Exposes the basic interface to interact with the serialization means."""

import json

import mnemic.dbconn as dbconn

DbConnection = dbconn.DbConnection

_SQL_INSERT_RUN = """
INSERT INTO tracing_run (uuid, app_name, column_names)  VALUES($1, $2, $3);
"""

_SQL_INSERT_ROW = """
INSERT INTO tracing_row (uuid, row_data) VALUES($1, $2);
"""

_SQL_SELECT_NUMBER_OF_COLS = """
SELECT CARDINALITY(column_names) AS col_count, uuid 
FROM tracing_run WHERE uuid=$1
"""

_SQL_SELECT_COL_NAMES = """
select unnest as col_name, ordinality -1 as index 
from unnest((select column_names from tracing_run where uuid=$1)) 
with ordinality
"""

_SQL_SELECT_LATEST_RUN = """
select uuid from tracing_run where app_name=$1 
order by creation_time desc limit 1
"""

_PREFETCH_SIZE = 100


async def process_message(conn_pool, payload):
    assert isinstance(payload, str)
    msg = json.loads(payload)
    msg_type = msg.get('msg_type')
    if msg_type == "create_trace_run":
        identifier = msg.get('uuid')
        app_name = msg.get('app_name')
        column_names = list(msg.get('column_names'))
        await _create_tracer(conn_pool, identifier, app_name, *column_names)
    elif msg_type == 'row':
        identifier = msg.get('uuid')
        row_data = msg.get('row_data')
        await insert_row(conn_pool, identifier, *row_data)


async def get_latest_trace(app_name):
    async with DbConnection() as conn_pool:
        async with conn_pool.acquire() as conn:
            stmt = await conn.prepare(_SQL_SELECT_LATEST_RUN)
            async with conn.transaction():
                async for record in stmt.cursor(app_name,
                                                prefetch=_PREFETCH_SIZE):
                    uuid = record['uuid']
        return await get_trace(uuid, conn_pool)


async def get_trace(uuid, conn_pool=None):
    if not conn_pool:
        async with DbConnection() as conn_pool:
            return await _get_trace(uuid, conn_pool)
    else:
        return await _get_trace(uuid, conn_pool)


async def _create_tracer(conn_pool, identifier, app_name, *column_names):
    """Creates a new run.

    :param str uuid: The uuid of the run expressed as string.
    :param str app_name: The application that is been traced.
    """
    async with conn_pool.acquire() as conn:
        await conn.execute(
            _SQL_INSERT_RUN,
            identifier,
            app_name,
            list(column_names))


async def insert_row(conn_pool, uuid, *row_data):
    async with conn_pool.acquire() as conn:
        await conn.execute(_SQL_INSERT_ROW, uuid, list(row_data))


async def _get_trace(uuid, conn_pool):
    assert uuid
    assert conn_pool
    col_names = []
    async with conn_pool.acquire() as conn:
        stmt = await conn.prepare(_SQL_SELECT_COL_NAMES)
        async with conn.transaction():
            async for record in stmt.cursor(uuid, prefetch=_PREFETCH_SIZE):
                col_names.append(record['col_name'])
        clauses = [
            f"row_data[{index + 1}] as {col_name}"
            for index, col_name in enumerate(col_names)
        ]
        sql = "select to_char(date_time, 'YYYY-MM-DD HH24:MI:SS') as timestamp , " + \
              ','.join(clauses) + \
              " from tracing_row where uuid=$1 order by 1"
        stmt = await conn.prepare(sql)

        lines = ['time,' + ','.join(col_names)]
        async with conn.transaction():
            async for record in stmt.cursor(uuid, prefetch=_PREFETCH_SIZE):
                values = [str(v) for v in list(dict(record).values())]
                lines.append(','.join(values))
        return '\n'.join(lines)
