"""Tests the utils module."""

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
        async with db_conn.DbConnection(conn_str=conn_str) as db:
            await utils.process_message(db=db, payload=msg)

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
        async with db_conn.DbConnection(conn_str=conn_str) as db:
            for msg in invalid_msgs:
                with self.assertRaises(exceptions.InvalidMessage):
                    await utils.process_message(db=db, payload=msg)

    @async_testable
    async def test_accessors(self):
        """Tests the accessor functions."""
        conn_str = await common.recreate_db(self.DB_NAME)
        utils.set_conn_str(conn_str)
        identifier = str(uuid.uuid4())
        app_name = 'testing_app'
        msg = {
            "msg_type": "create_trace_run",
            "app_name": app_name,
            "uuid": identifier,
            "column_names": ["v1", 'v2']
        }

        N = 10
        rows = [
            {
                "msg_type": "row",
                "uuid": identifier,
                "row_data": [random.uniform(0, 100), random.uniform(0, 100)]
            }
            for _ in range(N)
        ]

        self.assertEqual(len(rows), N)

        async with db_conn.DbConnection(conn_str=conn_str) as db:
            await utils.process_message(db=db, payload=msg)
            for row in rows:
                await utils.process_message(db=db, payload=row)

        msgs = await utils.get_trace_as_json(uuid=identifier)

        self.assertIn('time', msgs)
        self.assertIn('v1', msgs)
        self.assertIn('v2', msgs)

        self.assertEqual(len(msgs['time']), N)
        self.assertEqual(len(msgs['v1']), N)
        self.assertEqual(len(msgs['v2']), N)

        run_info = await utils.get_trace_run_info(identifier)

        self.assertIn('app_name', run_info)
        self.assertIn('counter', run_info)
        self.assertIn('started', run_info)
        self.assertIn('duration', run_info)

        latest_trace = await utils.get_latest_trace(app_name)

        self.assertIsInstance(latest_trace, str)

        traces = await utils.get_all_tracers()


if __name__ == '__main__':
    unittest.main()