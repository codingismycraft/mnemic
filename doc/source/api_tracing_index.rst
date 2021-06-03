.. _dolon-api-reference:

=================
Dolon tracing API
=================

The dolon API exposes the function to start a tracer and also several build
in profiling functions; custom profiling functions can also be added if needed.

Start a tracer
==============
A tracer is created and started using the *start_tracer* function which should
run in the background as an async coroutine.


.. autofunction:: dolon.trace_client.start_tracer


What is a Profiler Function
===========================

Any async callable that does not receive any argumenets and returns a numeric
value can be used as a *profiler function*.  For example if we want to profile
the size of a text file and monitor it in a tracer run we need a function
similar to this:

.. code-block:: python

    async def file_size(){
        return _get_file_size("the_file_to_check.txt")
    }


Generic build-in profilers
==========================
To make development easier for the client the following *profiler functions*
are supported out of the box:

.. autofunction:: dolon.trace_client.active_tasks

.. autofunction:: dolon.trace_client.cpu_percent

.. autofunction:: dolon.trace_client.virtual_memory_percent

.. autofunction:: dolon.trace_client.memory_use

Example using build-in profilers
=================================

The following code snippet shows how to write a tracer talking to a mnemic
backend on the localhost and listening to the 12013 port.

The profiling functions used are *mem_allocation*, *active_tasks* and
*cpu_percent*.

Note that tracemalloc should be initialized as early as possible in the import
list.

.. code-block:: python

    import tracemalloc
    tracemalloc.start()
    import dolon.trace_client as tc

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


The *tracer* function defined above should be scheduled from the running program
as follows:

.. code-block:: python

    asyncio.ensure_future(tracer())

PostgresSql profiler
====================
Used to profile the state of postgres database

.. autoclass:: dolon.trace_client.PostgresDiagnostics
   :members:

Example using PostgresDiagnostics
=================================

.. code-block:: python

    """Sample of postgres tracer."""

    import asyncio

    import tracemalloc
    tracemalloc.start()

    import dolon.trace_client as tc

    CONN_STR = f'postgresql://postgres:postgres123@127.0.0.1:15432/mnemic'


    async def tracer():
        """Plain vanilla tracer."""
        tracer_name = "profiling-db"
        host = "localhost"
        port = 12013
        frequency = 1
        async with tc.PostgresDiagnostics(conn_str=CONN_STR) as db_profiler:
            await tc.start_tracer(
                tracer_name,
                frequency,
                host,
                port,
                tc.mem_allocation,
                tc.active_tasks,
                tc.cpu_percent,
                db_profiler.idle,
                db_profiler.count_db_connections,
                db_profiler.live_msgs
            )


    async def main():
        """The main function to profile."""
        while 1:
            await asyncio.sleep(0.4)


    if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(tracer())
        loop.run_until_complete(main())

Profiling function
==================

If we have a callable (sync or async) that we need ot trace we can do so by
decorating it with the profiler function:

.. autofunction:: dolon.profiler.profiler

A callable that is decorated with the profiler *decorator8 will automatically
be added to the tracer without having to specify it explicitly when
calling the *start_tracer* function.

The *traces* that will be recorded are:

+------------------+----------------------------------------------------+
| Name             |  Desc                                              |
+------------------+----------------------------------------------------+
| Hits             |  Number of calls for the whole duration of the run |
+------------------+----------------------------------------------------+
| Active Instances |  Active instances per time                         |
+------------------+----------------------------------------------------+
| Average Time     |  The average completion time                       |
+------------------+----------------------------------------------------+

To remove all profiled functions we can use the *clear* function:

.. autofunction:: dolon.profiler.clear

Example of profiling a function
===============================

An example of profiling a function can be seen here:

(see *time_and_memory_consuming_func*)

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
        tracer_name = "profiling-db"
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

