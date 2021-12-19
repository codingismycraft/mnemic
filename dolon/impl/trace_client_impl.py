import aiohttp
import asyncio
import datetime
import json
import os
import socket
import tracemalloc
import uuid


class TraceClientImpl:

    def __init__(self, app_name, host, port, verbose, *diagnostics):
        self._app_name = app_name
        self._host = host
        self._port = port
        self._diagnostics = list(diagnostics)
        self._socket = None
        self._verbose = verbose

    def _send(self, data):
        assert self._socket
        assert isinstance(data, dict)
        data["uuid"] = self._uuid
        txt = json.dumps(data)
        self._socket.sendto(txt.encode('utf-8'), (self._host, self._port))

    async def run(self, frequency):
        while 1:
            await asyncio.sleep(frequency)
            msg = {
                "msg_type": "row",
                "row_data": [
                    await diagnostic() for diagnostic in self._diagnostics
                ]
            }
            if self._verbose:
                print("Sending:", msg)
            self._send(msg)

    async def __aenter__(self):
        tracemalloc.start()
        self._uuid = str(uuid.uuid4())
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        column_names = []
        for diagnostic in self._diagnostics:
            if hasattr(diagnostic, "__name__"):
                column_names.append(diagnostic.__name__)
            elif hasattr(diagnostic, "__class__"):
                column_names.append(diagnostic.__class__.__name__)
            else:
                raise ValueError

        msg = {
            "msg_type": "create_trace_run",
            "app_name": self._app_name,
            "column_names": column_names
        }
        self._send(msg)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._socket:
            self._socket.close()
            self._socket = None
            tracemalloc.stop()


class RabbitmqStats:
    """Lower level implementation to retrieve rabbitmq stats."""

    _connections = 0
    _channels = 0
    _queues = 0
    _bindings = 0
    _last_updated = None
    _lock = asyncio.Lock()
    _MIN_UPDATE_INTERVAL = 5
    _DEFAULT_RMQ_SERVER = "http://guest:guest@10.0.2.2:15672"

    @classmethod
    def _get_rmq_server(cls):
        """Returns the RMQ server to use.

        :returns: The RMQ server to use.
        :rtype: str
        """
        return os.environ.get("RMQ_SERVER", cls._DEFAULT_RMQ_SERVER)

    @classmethod
    def _get_min_update_interval(cls):
        return os.environ.get("MIN_RMQ_UPDATE_INTERVAL",
                              cls._MIN_UPDATE_INTERVAL)

    @classmethod
    async def _refresh(cls):
        async with cls._lock:
            now = datetime.datetime.now()
            try:
                if cls._last_updated is None or (
                        now - cls._last_updated).total_seconds() >= cls._MIN_UPDATE_INTERVAL:
                    async with aiohttp.ClientSession() as session:
                        server = cls._get_rmq_server()
                        async with session.get(f'{server}/api/queues') as resp:
                            if 200 <= resp.status < 299:
                                cls._queues = len(await resp.json())

                        async with session.get(f'{server}/api/connections') as resp:
                            if 200 <= resp.status < 299:
                                cls._connections = len(await resp.json())

                        async with session.get(f'{server}/api/channels') as resp:
                            if 200 <= resp.status < 299:
                                cls._channels = len(await resp.json())

                        async with session.get(
                                f'{server}/api/bindings') as resp:
                            if 200 <= resp.status < 299:
                                cls._bindings = len(await resp.json())
                    cls._last_updated = now
            except Exception as ex:
                pass

    @classmethod
    async def rabbitmq_connections(cls):
        """Returns the number of active rabbitmq connections.

        :returns: The number of active rabbitmq connections.

        :rtype: int.
        """
        await cls._refresh()
        return cls._connections

    @classmethod
    async def rabbitmq_channels(cls):
        """Returns the number of active rabbitmq channels.

        :returns: The number of active rabbitmq channels.

        :rtype: int.
        """
        await cls._refresh()
        return cls._channels

    @classmethod
    async def rabbitmq_queues(cls):
        """Returns the number of rabbitmq queues.

        :returns: The number of rabbitmq queues.

        :rtype: int.
        """
        await cls._refresh()
        return cls._queues

    @classmethod
    async def rabbitmq_bindings(cls):
        """Returns the number of rabbitmq bindings.

        :returns: The number of rabbitmq bindings.

        :rtype: int.
        """
        await cls._refresh()
        return cls._bindings
