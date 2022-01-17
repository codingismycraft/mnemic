"""Tests the utils module."""
import os
import random
import unittest
import uuid

import dolon.db_conn as db_conn
import dolon.exceptions as exceptions
import dolon.utils as utils
import dolon.tests.common as common

# Aliases.
async_testable = common.async_testable


class TestUtils(unittest.TestCase):
    """Tests the utils module.

    :cvar str DB_NAME: The name of the database to create.
    """

    DB_NAME = 'utils_test'

    @async_testable
    async def test_process_message(self):
        """Tests the process message function."""
        conn_str = await common.recreate_db(self.DB_NAME)
        identifier = str(uuid.uuid4())
        app_name = 'testing_app'
        msg = {
            "msg_type": "create_trace_run",
            "app_name": app_name,
            "uuid": identifier,
            "column_names": ["v1", 'v2']
        }
        os.environ["POSTGRES_CONN_STR"] = conn_str
        async with db_conn.DbConnection() as db:
            await utils.process_message(db=db, payload=msg)
        del os.environ["POSTGRES_CONN_STR"]

    @async_testable
    async def test_process_message_invalid_payload(self):
        """Tests the process message function with invalid payload."""
        conn_str = await common.recreate_db(self.DB_NAME)
        invalid_msgs = [
            {},
            {'msg_type': "create_trace_run"},
            {
                "msg_type": "create_trace_run",
                "app_name": 81,
                "uuid": 123,
                "column_names": ["v1", 'v2']
            }
        ]
        os.environ["POSTGRES_CONN_STR"] = conn_str
        async with db_conn.DbConnection() as db:
            for msg in invalid_msgs:
                with self.assertRaises(exceptions.InvalidMessage):
                    await utils.process_message(db=db, payload=msg)
        del os.environ["POSTGRES_CONN_STR"]


if __name__ == '__main__':
    unittest.main()
