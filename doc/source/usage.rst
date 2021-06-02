.. _dolon-examples:


dolon Usage
=============

The following is a plain vanilla program that creates a trace run:


.. code-block:: python

    """Mnemic hello_word program."""

    import asyncio
    import random

    import tracemalloc

    tracemalloc.start()

    import dolon.trace_client as tc
    import dolon.profiler as profiler


    async def tracer():
        """Plain vanilla tracer."""
        tracer_name = "hello-world"
        host = "localhost"
        port = 12013
        frequency = 1
        await tc.start_tracer(
            tracer_name,
            frequency,
            host,
            port,
            tc.mem_allocation,
            tc.active_tasks,
            tc.cpu_percent
        )

    @profiler.profiler
    async def time_and_memory_consuming_func():
        """Allocates some memory for some time!"""
        _ = [i for i in range(10000)]
        await asyncio.sleep(random.uniform(0.1, 3))


    async def main():
        """The main function to profile."""
        while 1:
            asyncio.ensure_future(time_and_memory_consuming_func())
            await asyncio.sleep(0.4)


    if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(tracer())
        loop.run_until_complete(main())



.. note::
    We assume that the host and port are accessible from the environment.
