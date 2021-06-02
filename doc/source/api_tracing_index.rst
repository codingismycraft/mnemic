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


Profiler Function
===================

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


PostgresSql profiler
====================
Used to profile the state of postgres database

.. autoclass:: dolon.trace_client.PostgresDiagnostics
   :members:
