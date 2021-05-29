"""Tests the get_all_tracers function."""

import asyncio
import os

import dolon.utils as utils

os.environ["POSTGRES_PASSWORD"] = "postgres123"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_DB"] = "mnemic"
os.environ["HOST"] = "127.0.0.1"


async def main():
    print(await utils.get_all_tracers())
    print(await utils.get_trace_run_info("187b85fa-346c-4707-9a82-a4613f8d8468"))

    #print(await utils.get_trace_as_json("187b85fa-346c-4707-9a82-a4613f8d8468"))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
