
.. github: https://en.wikipedia.org/wiki/Dolon_(mythology)

=================
Running locally
=================

To run the mnemic / dolon system locally you will need to have vagrant and git
installed. You can clone the code from github and start vagrant (answer yes
when prompted to install vagrant pluggins).

.. code-block:: bash

    git clone https://github.com/codingismycraft/mnemic.git
    cd mnemic
    vagrant up

Once vagrant is up you can now ssh to the box and prepare the environment:

.. code-block:: bash

    vagrant ssh
    cd /vagrant
    sudo pip3 setup.py develop
    cd ./db
    docker build -t my-db-image .
    docker run --name my-db -e POSTGRES_PASSWORD=postgres123 -p 5432:5432 -d my-db-image

At this point you should be able to access the local database **mnemic** which
holds the tracing runs:

.. code-block:: bash

    docker exec -it mnemic-db bash
    psql -U postgres mnemic

    mnemic=# \dt+
                                  List of relations
     Schema |    Name     | Type  |  Owner   | Persistence | Size  | Description
    --------+-------------+-------+----------+-------------+-------+-------------
     public | tracing_row | table | postgres | permanent   | 20 MB |
     public | tracing_run | table | postgres | permanent   | 72 kB |
    (2 rows)

Start the backend server:

.. code-block:: bash

    cd /vagrant/backend
    python3 server_dev.py

    >> DEBUG:asyncio:Using selector: EpollSelector
    >> INFO:root:Starting UDP server

Run the integration test:

    .. code-block:: bash

        cd /vagrant/backend/integration_tests
        python3 using_server.py

Start the front end:

    .. code-block:: bash

        cd/vagrant/frontend
        python3 server_dev.py

        >> ======== Running on http://0.0.0.0:8900 ========
        >>(Press CTRL+C to quit)

Access the frond end from a browser using the address **http://localhost:6900/**

Start the jupyter notebook if you want to do some further data mining:

.. code-block:: bash

    cd /vagrant/analytics/
    jupyter notebook --ip='*' --port 8888  --NotebookApp.token='' --NotebookApp.password='' --allow-root > error.log &

Access jupyter notebook from the browser using **localhost:6888**