"""Sample of using server to create a trace."""

import asyncio

import dolon.trace_client as tc


_CONN_STR =  f'postgresql://postgres:postgres123@127.0.0.1:5432/mnemic'


async def main():
    host = "127.0.0.1"
    port = 12012
    async with tc.MemoryDiagnostics() as mem_diag, tc.PostgresDiagnostics(conn_str=_CONN_STR) as db_diag:
        await tc.start_tracer(
            "Jane", 1, host, port,
            mem_diag.mem_allocation,
            tc.active_tasks,
            db_diag.live_msgs
        )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
