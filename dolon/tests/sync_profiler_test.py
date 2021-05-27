"""Tests the profiler module."""

import asyncio
import time
import random

import dolon.profiler as profiler


class RetrieveInfo:

    @profiler.profiler
    def retriever(self):
        time.sleep(0.01)

    @profiler.profiler
    def clear(self):
        time.sleep(0.01)


@profiler.profiler
def foo():
    time.sleep(0.2)


def main():
    """Tests a full run."""
    ri = RetrieveInfo()

    for _ in range(2):
        ri.retriever()
        ri.clear()
        foo()

    for name in profiler.get_profiling_callables():
        print(name)
        print(f'hits: {profiler.get_hits(name)}')
        print(f'avgdur: {profiler.get_average_time(name)}')
        print(f'inst: {profiler.get_active_instances(name)}')

    print(profiler.get_profiling_callables())



    for profilying_foo in profiler.get_profiling_functions():
        print(profilying_foo.__name__, profilying_foo())


if __name__ == '__main__':
    main()
