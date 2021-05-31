"""The listening UDP server for tracing messages."""

import asyncio
import os
import signal

import logging

import dolon.utils as utils
import dolon.db_conn as db_conn

logging.basicConfig(level=logging.DEBUG)

server_port = int(os.environ["BACK_END_PORT"])

class CustomMsgProtocol(asyncio.BaseProtocol):
    _db = None

    @classmethod
    def set_db(cls, db):
        cls._db = db

    def datagram_received(self, data, addr):
        message = data.decode()
        asyncio.ensure_future(
            utils.process_message(db=self._db, payload=message)
        )

async def run():
    stop_event = asyncio.Event()
    loop = asyncio.get_event_loop()
    await loop.create_datagram_endpoint(
        CustomMsgProtocol,
        local_addr=('0.0.0.0', server_port)
    )

    async def terminate():
        stop_event.set()
        await asyncio.sleep(2)

    loop = asyncio.get_event_loop()
    for signal_to_overwrite in ('SIGTERM', 'SIGINT'):
        loop.add_signal_handler(
            getattr(signal, signal_to_overwrite),
            lambda: asyncio.ensure_future(
                terminate()
            )
        )
    logging.info("Starting UDP server")
    async with db_conn.DbConnection() as db:
        CustomMsgProtocol.set_db(db)
        await stop_event.wait()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
