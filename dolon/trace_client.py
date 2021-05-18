import socket
import json


class TraceClient:
    def __init__(self, app_name, uuid, ip, port, *columns):
        self._app_name = app_name
        self._uuid = uuid
        self._columns = list(columns)
        self._ip = ip
        self._port = port
        self._socket = None

    def send(self, data):
        assert self._socket
        assert isinstance(data, dict)
        txt = json.dumps(data)
        self._socket.sendto(txt.encode('utf-8'), (self._ip, self._port))

    async def __aenter__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        msg = {
            "msg_type": "create_trace_run",
            "app_name": self._app_name,
            "uuid": self._uuid,
            "column_names": self._columns
        }
        self.send(msg)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._socket:
            self._socket.close()
            self._socket = None

