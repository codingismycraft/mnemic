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

    # print('==')
    # print(profiler.get_profiling_callables())
    # for profilying_foo in profiler.get_profiling_functions():
    #     print(profilying_foo.__name__, profilying_foo())
    # print('==')

    ri = RetrieveInfo()

    for _ in range(2):
        ri.retriever()
        ri.clear()
        foo()

    print('==')
    for profilying_foo in profiler.get_profiling_functions():
        print(profilying_foo.__name__, profilying_foo())
    print('==')


if __name__ == '__main__':
    main()
