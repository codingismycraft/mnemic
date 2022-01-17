"""Sample of using server to create a trace."""

import asyncio
import random

import tracemalloc

tracemalloc.start()

import dolon.trace_client as tc
import dolon.profiler as profiler
import dolon.speedometer as speedometer

_CONN_STR = f'postgresql://postgres:postgres123@127.0.0.1:5432/mnemic'

total_calls = 0

total_calls_speedometer = speedometer.Speedometer()


async def total_calls_speed():
    return await total_calls_speedometer.get_speed(total_calls)


@profiler.profiler
async def foo():
    await asyncio.sleep(random.uniform(0.1, 3))


@profiler.profiler
async def goo():
    await asyncio.sleep(random.uniform(0.1, 3))


async def backend_process():
    global total_calls

    junk = Junk()
    while True:
        asyncio.ensure_future(foo())
        asyncio.ensure_future(goo())
        await asyncio.sleep(0.1)
        await junk.junk()
        total_calls += 1


class Junk:
    @profiler.profiler
    async def junk(self):
        await asyncio.sleep(random.uniform(0.01, 0.2))


async def main():
    tracer_name = "using-speedometer-1"
    frequency = 1
    host = "127.0.0.1"
    port = 12012
    verbose = True

    async with tc.PostgresDiagnostics(conn_str=_CONN_STR) as db_profiler:
        await tc.start_tracer(
            tracer_name,
            frequency,
            host,
            port,
            verbose,
            tc.mem_allocation,
            db_profiler.idle,
            db_profiler.count_db_connections,
            db_profiler.live_msgs,
            total_calls_speed
        )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(backend_process())
    loop.run_until_complete(main())
