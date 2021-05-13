"""Integration testing for mnemic."""

import asyncio
import os
import uuid
import random

import mnemic.utils as utils


# Create the testing database.
# dir_path = os.path.dirname(os.path.realpath(__file__))
# dir_path = os.path.join(dir_path, '..', 'db')
# os.system(f"cd {dir_path};./create-db.sh {DB_NAME}; cd ~")


async def create_rows(conn_pool, identifier):
    for _ in range(2000):
        await utils.insert_row(
            conn_pool,
            identifier,
            random.uniform(0, 100),
            random.uniform(0, 100)
        )


async def main():
    async with utils.DbConnection() as conn_pool:
        identifier = str(uuid.uuid4())
        await utils._create_tracer(conn_pool, identifier, "junk", "v1", 'v2')
        await create_rows(conn_pool, identifier)
        print(await utils.get_latest_trace('junk'))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
