"""Integration testing for mnemic."""

import asyncio
import os
import uuid
import random

import dolon.utils as utils
import dolon.db_conn as db_conn


os.environ["POSTGRES_PASSWORD"] = "postgres123"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_DB"] = "mnemic"
os.environ["HOST"] = "127.0.0.1"

async def main():
    async with db_conn.DbConnection() as conn_pool:
        identifier = str(uuid.uuid4())
        app_name = 'junk'

        msg = {
            "msg_type": "create_trace_run",
            "app_name": app_name,
            "uuid": identifier,
            "column_names": ["v1", 'v2']
        }

        await utils.process_message(conn_pool, msg)

        for _ in range(20):
            msg = {
                "msg_type": "row",
                "uuid": identifier,
                "row_data": [random.uniform(0, 100), random.uniform(0, 100)]
            }

            await utils.process_message(conn_pool, msg)

        print(await utils.get_latest_trace('junk'))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())