"""Runs the server locally."""

import asyncio
import os

import backend.server as server

os.environ["POSTGRES_PASSWORD"] = "postgres123"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_DB"] = "mnemic"
os.environ["HOST"] = "127.0.0.1"

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.run())

