"""Implements tesing utilities."""

import asyncio
import os

import dolon.db_conn as db_conn

_SQL_DROP_DB = 'DROP DATABASE IF EXISTS {db_name}'.format
_SQL_CREATE_DB = 'CREATE database {db_name}'.format


def async_testable(foo):
    """Quick and dirty function to allow for tesing of async functions.

    :param coro foo: The async function to test.
    """

    def test_inner(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(foo(*args, **kwargs))

    test_inner.__name__ = foo.__name__
    return test_inner


def get_conn_str(db_name):
    """Returns the connection string for the passed in database."""

    return f'postgresql://postgres:postgres123@localhost:5432/{db_name}'


async def recreate_db(db_name):
    """Recreates the database for the passed in name.

    :param str db_name: The name of the database to create.

    :returns: The connection string to the database that was created.
    :rtype: str
    """
    assert db_name.strip() != 'mnemic'
    conn_str = get_conn_str('postgres')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sql_schema_file = os.path.join(dir_path, '..', '..', 'db', 'create-db.sql')

    with open(sql_schema_file) as f:
        sql_schema_script = f.read()

    db_conn.DbConnection.set_conn_str(conn_str)
    async with db_conn.DbConnection() as db:
        conn_pool = db.get_conn_pool()
        async with conn_pool.acquire() as conn:
            await conn.execute(_SQL_DROP_DB(db_name=db_name))
            await conn.execute(_SQL_CREATE_DB(db_name=db_name))

    conn_str = get_conn_str(db_name)
    db_conn.DbConnection.set_conn_str(conn_str)
    async with db_conn.DbConnection() as db:
        conn_pool = db.get_conn_pool()
        async with conn_pool.acquire() as conn:
            await conn.execute(sql_schema_script)
    db_conn.DbConnection.set_conn_str(None)
    return conn_str
