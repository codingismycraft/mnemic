"""Runs the server locally."""

import asyncio
import os

_CONN_STR = f'postgresql://postgres:postgres123@localhost:5432/mnemic'
os.environ["POSTGRES_CONN_STR"] = _CONN_STR
os.environ["BACK_END_PORT"] = "12012"

import backend.server as server

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.run())
