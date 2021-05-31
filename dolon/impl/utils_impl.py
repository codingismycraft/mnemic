"""Implementation details to interact with the serialization means."""

import datetime
import json
import math

import dolon.db_conn as db_conn
import dolon.exceptions as exceptions
import dolon.impl.constants as constants

# Aliases.
DbConnection = db_conn.DbConnection

_PREFETCH_SIZE = 100


async def process_message(db, payload):
    """Processes a tracing message storing it to the db.

    :param db: The database object to use.

    :param dict payload: A dict representing the message to store.

    Can be either a tracing run creation in the form of:

        msg = {
            "msg_type": "create_trace_run",
            "app_name": app_name,
            "uuid": identifier,
            "column_names": ["v1", 'v2']
        }

    or for the insertion of a tracing row:

        msg = {
            "msg_type": "row",
            "uuid": identifier,
            "row_data": [12.2, 123.1]
        }

    raises: InvalidMessage
    """
    if not isinstance(payload, dict):
        assert isinstance(payload, str)
        msg = json.loads(payload)
    else:
        msg = payload
    # logging.info(str(payload)) # Will cause missed messages.
    msg_type = msg.get('msg_type')
    try:
        if msg_type == "create_trace_run":
            identifier = msg.get('uuid')
            app_name = msg.get('app_name')
            column_names = msg.get('column_names')
            if not all([identifier, app_name, column_names]):
                raise exceptions.InvalidMessage(
                    f"Message not supported: {str(payload)}"
                )
            column_names = list(column_names)
            await _create_tracer(db, identifier, app_name, *column_names)
        elif msg_type == 'row':
            identifier = msg.get('uuid')
            row_data = msg.get('row_data')
            await _insert_row(db, identifier, *row_data)
        else:
            raise exceptions.InvalidMessage(
                f"Message not supported: {str(payload)}"
            )
    except Exception as ex:
        raise exceptions.InvalidMessage(
            f"Message not supported: {str(payload)}"
        ) from ex


async def get_trace_as_json(uuid):
    """Returns all the tracing rows for the passed in uuid as json.

    :param str uuid: The identifier for the trace run.

    :returns: All the tracing rows for the passed in uuid as json.
    :rtype: list[dict]
    """
    data = await get_trace(uuid)
    lines = data.split('\n')
    field_names = lines[0].split(',')
    columns = [list() for _ in range(len(field_names))]

    for line in lines[1:]:
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
    """Returns descriptive info for the passed in uuid.

    :param str uuid: The identifier for the trace run.

    :returns: Descriptive info for the passed in uuid.
    :rtype: dict
    """
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
                    creation_time = _format_datetime(record['creation_time'])
            stmt = await conn.prepare(constants.SQL_SELECT_RUN_INFO)
            async with conn.transaction():
                async for record in stmt.cursor(uuid,
                                                prefetch=_PREFETCH_SIZE):
                    counter = record['counter']
                    from_time = record['from_time']
                    to_time = record['to_time']

    if to_time is None or from_time is None:
        # There are no rows for this run
        counter = 0
        started = creation_time
        duration = 'n/a'
    else:
        started = creation_time
        duration = _get_duration(to_time, from_time)
    return {
        'app_name': app_name,
        'counter': f'{counter:,}',
        'started': started,
        'duration': duration
    }


async def get_latest_trace(app_name):
    """Returns the latest trace for the passed in app_name.

    :return: A list of objects.
    """
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
    """Returns all the tracing rows for the passed in uuid.

    :param str uuid: The identifier for the trace run.

    :returns: A list of strings representing a csv view of the tracing run.
    :rtype: list[str]
    """
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


async def _insert_row(db, uuid, *row_data):
    """Inserts a tracing row to the database.

    :param db: The database object to use.
    :param str uuid: The identifier for the trace run.
    :param row_data: Represent the values for each data point.
    """
    conn_pool = db.get_conn_pool()
    async with conn_pool.acquire() as conn:
        await conn.execute(constants.SQL_INSERT_ROW, uuid, list(row_data))


async def _get_trace(uuid, db):
    """Returns all the tracing rows for the passed in uuid.

    :param str uuid: The identifier for the trace run.

    :returns: A list of strings representing a csv view of the tracing run.
    :rtype: list[str]
    """
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
                creation_date = record['creation_time']
                tracer_runs.append(
                    {
                        'creation_time': _format_datetime(creation_date),
                        'uuid': record['uuid'],
                    }

                )
    return tracer_runs


def _get_duration(start_time, end_time):
    """Returns the duration from t1 to t2.

    :param datetime.datetime start_time: Start time.
    :param datetime.datetime end_time: End time.

    :return: The duration as a string.
    :rtype: str
    """
    diff = int(math.fabs(int((start_time - end_time).total_seconds())))

    days = diff // constants.DAY_IN_SECONDS
    diff -= days * constants.DAY_IN_SECONDS

    hours = diff // constants.HOUR_IN_SECONDS
    diff -= hours * constants.HOUR_IN_SECONDS

    minutes = diff // constants.MINUTE_IN_SECONDS
    diff -= minutes * constants.MINUTE_IN_SECONDS

    seconds = diff

    tokens = []
    if days:
        tokens.append(f"{days} days")
    if hours:
        tokens.append(f"{hours} hours")
    if minutes:
        tokens.append(f"{minutes} min")
    if seconds:
        tokens.append(f"{seconds} secs")

    return ', '.join(tokens)


def _format_datetime(date_to_format):
    """Formats the passed in date time.

    :param: datetime.datetime date_to_format: The date to format.

    :return: The formatted date.
    :rtype: str
    """
    current_year = datetime.datetime.now().year
    if date_to_format.year == current_year:
        return date_to_format.strftime("%a, %b %d, %H:%M")
    else:
        return date_to_format.strftime("%a, %b %d %Y, %H:%M")
