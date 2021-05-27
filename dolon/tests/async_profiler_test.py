"""Tests the profiler module."""

import asyncio

import dolon.profiler as profiler


@profiler.profiler
async def goo():
    await asyncio.sleep(2)


async def main():
    """Tests a full run."""

    tasks = [goo() for _ in range(200)]
    await asyncio.gather(*tasks)

    for name in profiler.get_profiling_callables():
        print(name)
        print(f'hits: {profiler.get_hits(name)}')
        print(f'avgdur: {profiler.get_average_time(name)}')
        print(f'inst: {profiler.get_running_instances(name)}')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
