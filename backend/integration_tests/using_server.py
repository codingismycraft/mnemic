import asyncio
import random
import uuid

import backend.trace_client as trace_client


async def main():
    identifier = str(uuid.uuid4())

    ip = "127.0.0.1"
    port = 9999

    column_names = ["col1", "col2"]
    async with trace_client.TraceClient("another junk", identifier, ip, port,
                                        *column_names) as client:
        for _ in range(2000):
            msg = {
                "msg_type": "row",
                "uuid": identifier,
                "row_data": [random.uniform(0, 100), random.uniform(0, 100)]
            }
            print("Sending:", msg)
            client.send(msg)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
