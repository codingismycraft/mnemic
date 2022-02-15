.. _The name Dolon: https://en.wikipedia.org/wiki/Dolon_(mythology)

.. _Mnemic: https://www.collinsdictionary.com/us/dictionary/english/mnemic

.. _documentation: https://mnemic.readthedocs.io/en/main/index.html


============
Introduction
============

Read here for full `documentation`_


Dolon
-----

`The name Dolon`_ comes from a spy in Homer's Iliad.

**dolon** is a library that interfaces with the mnemic service to trace real
time data; requires Python 3.6 or later and talks to the *mnemic* service that
must be running in an accessible host.

**dolon**'s recommended way to install it is to use **pip**:

.. code-block:: bash

    pip install dolon


Mnemic
------

`Mnemic`_ refers to the ability to retain memory.

**mnemic** is the backend that dolon talks to and also exposes the related
front end as a web page.  The easiest way to install it is using docker.

.. code-block:: bash

        docker run --name mnemic-db -e POSTGRES_PASSWORD=postgres123 -p 15432:5432 -d jpazarzis/mnemic-db
        docker run --name mnemic-back-end --add-host host.docker.internal:host-gateway -p 12013:12013/udp  -e POSTGRES_CONN_STR='postgresql://postgres:postgres123@172.17.0.1:15432/mnemic' -e BACK_END_PORT='12013'  -d jpazarzis/mnemic-backend
        docker run --name mnemic-front-end -e POSTGRES_CONN_STR='postgresql://postgres:postgres123@172.17.0.1:15432/mnemic'  -e FRONT_END_PORT='12111' -p 12111:12111  -d jpazarzis/mnemic-front-end

To run mnemic using docker-compose:

Note: by default, docker-compose will use `docker-compose.yml` located in the directory where it is executed from. To specify an alternate compose file, use: `-f, --file FILE`


sudo docker-compose up -d

this will start Mnemic Backend and Frontend containers in the background.

before running it make sure `POSTGRES_CONN_STR` var is exported as it is used to connect to RDS DB:


Verify that containers are running:

sudo docker-compose ps

docker-compose ps
      Name                    Command              State                      Ports                    
-------------------------------------------------------------------------------------------------------
mnemic_backend_1    python server.py               Up      0.0.0.0:12013->12013/udp,:::12013->12013/udp
mnemic_frontend_1   tini -g -- python3 server.py   Up      0.0.0.0:80->80/tcp,:::80->80/tcp, 8888/tcp  



To restart or shutdown the containers run:

sudo docker-compose restart

sudo docker-compose stop

High level View
---------------

The following picture shows the components that are involved in mnemic:

.. image:: https://user-images.githubusercontent.com/5374948/120810011-a864d700-c518-11eb-8fd2-12995b5e67c5.png
    :width: 400
    :alt: high level view


The backend consists of a service that runs as a docker container. It receives
messages from the application to profile and stores then in the database. It also exposes a UI client making the profiling data discoverable and visible by a browser session.


Quick Example
-------------

.. code-block:: python

    """Mnemic hello_word program."""

    import asyncio
    import random

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




After running the above program for several minutes the screen that we will
see when accessing the UI from the browser using **localhost:12111** will
be similar to the following:

.. image:: https://user-images.githubusercontent.com/67707281/120404061-84847400-c313-11eb-8c7b-9b6c629d4c67.png
    :width: 400

If we stop and restart the program then as we can see in the following picture
we will see another key in the tree control under the same trace run
name (hello-world in our example) which will acculate the new tracing info:

.. image:: https://user-images.githubusercontent.com/67707281/120406727-88b39000-c319-11eb-93b7-875f1ee96f19.png
    :width: 400
