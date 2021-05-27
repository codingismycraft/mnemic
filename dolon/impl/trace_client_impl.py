import asyncio
import socket
import json
import tracemalloc
import uuid

class TraceClientImpl:

    def __init__(self, app_name, host, port, *diagnostics):
        self._app_name = app_name
        self._host = host
        self._port = port
        self._diagnostics = list(diagnostics)
        self._socket = None

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
