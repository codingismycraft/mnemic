import asyncio
import signal

import mnemic.dbconn as dbconn
import mnemic.utils as utils


class CustomMsgProtocol(asyncio.BaseProtocol):
    _conn = None

    @classmethod
    def set_db_conn(cls, conn):
        cls._conn = conn

    def datagram_received(self, data, addr):
        message = data.decode()
        print("processing: ", message)
        asyncio.ensure_future(
            utils.process_message(conn_pool=self._conn, payload=message)
        )


async def run():
    stop_event = asyncio.Event()
    loop = asyncio.get_event_loop()

    # One instance of CustomMsgProtocol will be created per client.
    await loop.create_datagram_endpoint(
        CustomMsgProtocol,
        local_addr=('127.0.0.1', 9999)
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
    print("Starting UDP server")
    async with dbconn.DbConnection() as conn:
        CustomMsgProtocol.set_db_conn(conn)
        await stop_event.wait()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
