"""Local version of the front end server."""

import os

_CONN_STR = f'postgresql://postgres:postgres123@localhost:5432/mnemic'
os.environ["POSTGRES_CONN_STR"] = _CONN_STR
os.environ["FRONT_END_PORT"] = "8900"

import frontend.server as server


if __name__ == '__main__':
    server.run()
