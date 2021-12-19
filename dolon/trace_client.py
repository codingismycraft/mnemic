"""The trace client to record diagnostics."""

import asyncio
import logging
import os
import tracemalloc

import psutil

import dolon.profiler as profiler
import dolon.impl.db_conn_impl as db_conn_impl
import dolon.impl.db_stats as db_stats
import dolon.impl.trace_client_impl as trace_client_impl

_logger = logging.getLogger(__name__)


async def start_tracer(app_name, frequency, host, port, verbose, *diagnostics):
    """Starts a tracer.

    This is where a tracer is created and starts running in the background. It
    creates a new tracing run with the passed in app_name.

    If other tracing runs with the same name already exists then a new run
    will be created based on the start time without affecting them; doing so
    we keep history untouched and we can view any run from the front end based
    on the combination of app name and creation time.

    If an exception will be caught it will be logged and the application will
    stop.

    Note that all the profile-able functions will be added to diagnostics
    automatically.

    :param str app_name: The application name that will tag the trace.

    :param int frequency: The sleep interval between consecutive traces.

    :param str host: The host of the mnemic service.

    :param int port: The port that is listening for messages.

    :param bool verbose: True to print a message every time a msg is produced.

    :param diagnostics: The diagnostic callable to record. There is no limit
        in the number of diagnostic function to pass and they can differ from
        run to run for the same tracer name. The name of the callable will be
        used to store it and show it from mnemic's front end.
    """
    diagnostics = list(diagnostics) + profiler.get_profiling_functions(True)
    try:
        tc = trace_client_impl.TraceClientImpl(
            app_name,
            host,
            port,
            verbose,
            *diagnostics
        )
        async with tc:
            await tc.run(frequency)
    except Exception as ex:
        _logger.exception(ex)
        exit(-1)


class PostgresDiagnostics(db_conn_impl.DbConnectionImpl):
    """Wraps memory diagnostics within an async context manager.

    Must be used as a context manager; its profiler functions can be passed
    as diagnostics to start_tracer.

    :ivar str conn_str: The connection string to the database.
    """

    def __init__(self, conn_str):
        """Initializer.

        :param str conn_str: The connection string to the psql database.
        """
        super().__init__(min_size=1, max_size=1, conn_str=conn_str)

    async def live_msgs(self):
        """Returns the number of live messages in db.

        :returns: The number of live messages in db. Can be used as a profiler
            function.

        :rtype: async callable.
        """
        return await db_stats.live_msgs_in_db.get_value(self)

    async def dead_msgs(self):
        """Returns the number of dead messages in db.

        :returns: The number of dead messages in db. Can be used as a profiler
            function.

        :rtype: async callable.
        """
        return await db_stats.dead_msgs_in_db.get_value(self)

    async def idle(self):
        """Returns the number of idle sessions in db.

        :returns: The number of idle messages in db. Can be used as a profiler
            function.

        :rtype: async callable.
        """
        return await db_stats.idle_in_db.get_value(self)

    async def count_db_connections(self):
        """Returns the number of connections in db.

        :returns: The number of connections in db. Can be used as a profiler
            function.

        :rtype: async callable.
        """
        return await db_stats.conn_count_in_db.get_value(self)


async def mem_allocation():
    """Returns the size of the allocated memory in Mb.

    Assumes that the client code has already called tracemalloc.start().

    :returns: The memory allocation in Mb. Can be used as a profiler
            function.

    :rtype: int.
    """
    current, peak = tracemalloc.get_traced_memory()
    return current / 10 ** 6


async def active_tasks():
    """Returns the number of active async tasks.

    :returns: The number of active async tasks.

    :rtype: int.
    """
    return len([task for task in asyncio.Task.all_tasks() if not task.done()])


async def cpu_percent():
    """Returns the CPU usage percent.

    :returns: The CPU usage percent.

    :rtype: float.
    """
    return psutil.cpu_percent()


async def virtual_memory_percent():
    """Returns the virtual memory percentage usage.

    :returns: The virtual memory percentage usage.

    :rtype: float.
    """
    return psutil.virtual_memory().percent


async def memory_use():
    """Returns the memory usage.

    :returns: The memory usage.

    :rtype: float.
    """
    pid = os.getpid()
    py = psutil.Process(pid)
    return py.memory_info()[0] / 2. ** 30


async def rabbitmq_connections():
    """Returns the number of active rabbitmq connections.

    Use the RMQ_SERVER environment variable to customize the RMQ server.
    Use the MIN_RMQ_UPDATE_INTERVAL variable to customize the update timespan.

    :returns: The number of active rabbitmq connections.

    :rtype: int.
    """
    return await trace_client_impl.RabbitmqStats.rabbitmq_connections()


async def rabbitmq_channels():
    """Returns the number of active rabbitmq channels.

    Use the RMQ_SERVER environment variable to customize the RMQ server.
    Use the MIN_RMQ_UPDATE_INTERVAL variable to customize the update timespan.

    :returns: The number of active rabbitmq channels.

    :rtype: int.
    """
    return await trace_client_impl.RabbitmqStats.rabbitmq_channels()


async def rabbitmq_queues():
    """Returns the number of rabbitmq queues.

    Use the RMQ_SERVER environment variable to customize the RMQ server.
    Use the MIN_RMQ_UPDATE_INTERVAL variable to customize the update timespan.

    :returns: The number of rabbitmq queues.

    :rtype: int.
    """
    return await trace_client_impl.RabbitmqStats.rabbitmq_queues()


async def rabbitmq_bindings():
    """Returns the number of rabbitmq bindings.

    Use the RMQ_SERVER environment variable to customize the RMQ server.
    Use the MIN_RMQ_UPDATE_INTERVAL variable to customize the update timespan.

    :returns: The number of rabbitmq bindings.

    :rtype: int.
    """
    return await trace_client_impl.RabbitmqStats.rabbitmq_bindings()
