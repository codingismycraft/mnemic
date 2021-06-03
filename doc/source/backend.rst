.. _mnemic-backend-examples:


Mnemic Backend Installation
============================

Assuming that docker is available you can start mnemic's back end by executing
the following commands:


.. code-block:: bash

        docker run --name mnemic-db -e POSTGRES_PASSWORD=postgres123 -p 15432:5432 -d jpazarzis/mnemic-db
        docker run --name mnemic-back-end --add-host host.docker.internal:host-gateway -p 12013:12013/udp  -e POSTGRES_CONN_STR='postgresql://postgres:postgres123@172.17.0.1:15432/mnemic' -e BACK_END_PORT='12013'  -d jpazarzis/mnemic-backend
        docker run --name mnemic-front-end -e POSTGRES_CONN_STR='postgresql://postgres:postgres123@172.17.0.1:15432/mnemic'  -e FRONT_END_PORT='12111' -p 12111:12111  -d jpazarzis/mnemic-front-end



.. note::

    We assume that the host and port are accessible from the environment.
