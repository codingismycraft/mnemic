"""Exposes the basic interface to interact with the serialization means."""

import datetime
import io
import json
import time

import pandas as pd

import dolon.impl.constants as constants
import dolon.db_conn as db_conn

# Aliases.
DbConnection = db_conn.DbConnection

_PREFETCH_SIZE = 100

import logging


async def process_message(db, payload):
    if not isinstance(payload, dict):
        assert isinstance(payload, str)
        msg = json.loads(payload)
    else:
        msg = payload
    # logging.info(str(payload)) # Will cause missed messages.
    msg_type = msg.get('msg_type')
    if msg_type == "create_trace_run":
        identifier = msg.get('uuid')
        app_name = msg.get('app_name')
        column_names = list(msg.get('column_names'))
        await _create_tracer(db, identifier, app_name, *column_names)
    elif msg_type == 'row':
        identifier = msg.get('uuid')
        row_data = msg.get('row_data')
        await insert_row(db, identifier, *row_data)


async def get_latest_trace(app_name):
    async with DbConnection() as db:
        conn_pool = db.get_conn_pool()
        async with conn_pool.acquire() as conn:
            stmt = await conn.prepare(constants.SQL_SELECT_LATEST_RUN)
            async with conn.transaction():
                async for record in stmt.cursor(app_name,
                                                prefetch=_PREFETCH_SIZE):
                    uuid = record['uuid']
        return await _get_trace(uuid, db)


async def get_trace(uuid):
    async with DbConnection() as db:
        return await _get_trace(uuid, db)


async def _create_tracer(db, identifier, app_name, *column_names):
    """Creates a new run.

    :param str uuid: The uuid of the run expressed as string.
    :param str app_name: The application that is been traced.
    """
    conn_pool = db.get_conn_pool()
    async with conn_pool.acquire() as conn:
        await conn.execute(
            constants.SQL_INSERT_RUN,
            identifier,
            app_name,
            list(column_names))


async def insert_row(db, uuid, *row_data):
    conn_pool = db.get_conn_pool()
    async with conn_pool.acquire() as conn:
        await conn.execute(constants.SQL_INSERT_ROW, uuid, list(row_data))


async def _get_trace(uuid, db):
    conn_pool = db.get_conn_pool()
    assert uuid
    assert conn_pool
    col_names = []
    async with conn_pool.acquire() as conn:
        stmt = await conn.prepare(constants.SQL_SELECT_COL_NAMES)
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


async def get_trace_as_json(uuid):
    data = await get_trace(uuid)
    lines = data.split('\n')
    field_names = lines[0].split(',')
    columns = [list() for _ in range(len(field_names))]

    for line in lines[1:-1]:
        fields = line.split(',')
        for index, value in enumerate(fields):
            try:
                columns[index].append(float(value))
            except ValueError:
                columns[index].append(value)

    trace_as_json = {}
    for field_name, values in zip(field_names, columns):
        trace_as_json[field_name] = values

    return trace_as_json


async def get_trace_run_info(uuid):
    app_name = None
    counter = None
    from_time = None
    to_time = None

    async with DbConnection() as db:
        conn_pool = db.get_conn_pool()
        async with conn_pool.acquire() as conn:
            stmt = await conn.prepare(constants.SQL_SELECT_APP_NAME)
            async with conn.transaction():
                async for record in stmt.cursor(uuid,
                                                prefetch=_PREFETCH_SIZE):
                    app_name = record['app_name']

            stmt = await conn.prepare(constants.SQL_SELECT_RUN_INFO)
            async with conn.transaction():
                async for record in stmt.cursor(uuid,
                                                prefetch=_PREFETCH_SIZE):
                    counter = record['counter']
                    from_time = record['from_time']
                    to_time = record['to_time']
    total_secs = (to_time - from_time).total_seconds()

    return {
        'app_name': app_name,
        'counter': counter,
        'started': from_time.strftime("%b %d %Y %H:%M:%S"),
        'duration': time.strftime("%H hours %M minutes %S seconds", time.gmtime(total_secs))
    }
