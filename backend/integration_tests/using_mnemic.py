"""Integration testing for mnemic."""

import asyncio
import os
import uuid
import random

import dolon.utils as utils
import dolon.db_conn as db_conn

_CONN_STR = f'postgresql://postgres:postgres123@localhost:5432/mnemic'
os.environ["POSTGRES_CONN_STR"] = _CONN_STR


async def main():
    async with db_conn.DbConnection() as db:
        identifier = str(uuid.uuid4())
        app_name = 'john - doe'
        msg = {
            "msg_type": "create_trace_run",
            "app_name": app_name,
            "uuid": identifier,
            "column_names": ["v1", 'v2']
        }
        await utils.process_message(db, msg)
        for _ in range(20):
            msg = {
                "msg_type": "row",
                "uuid": identifier,
                "row_data": [random.uniform(0, 100), random.uniform(0, 100)]
            }
            await utils.process_message(db, msg)
        print(await utils.get_latest_trace('junk'))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
