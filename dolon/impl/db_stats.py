"""Exposes the postgress stats."""

_SQL_LIVE_MSGS = """
    select 
        sum(n_live_tup) as counter 
    from 
        pg_stat_user_tables;
"""

_SQL_DEAD_MSGS = """
    select  
        sum(n_dead_tup) as counter 
    from 
        pg_stat_user_tables;
"""

_SQL_IDLE_TRANS = """
SELECT count(*) as counter FROM pg_stat_activity  WHERE state = 'idle';
"""

_SQL_NUMBER_OF_CONNECTIONS = """
SELECT sum(numbackends) as counter FROM pg_stat_database;
"""


class _DbStat:
    """Encapsulates the details for a psql stat."""

    def __init__(self, sql):
        """Initializer.

        :param str sql: The SQL statement to retrieve the stats.
        """
        self._sql = sql

    async def get_value(self, db):
        """Returns the statistic from the passed in database.

        :param DbConnectionImpl db: The db connection object.
        """
        async for value in db.execute_query(self._sql):
            return float(value["counter"])


live_msgs_in_db = _DbStat(_SQL_LIVE_MSGS)
dead_msgs_in_db = _DbStat(_SQL_DEAD_MSGS)
idle_in_db = _DbStat(_SQL_IDLE_TRANS)
conn_count_in_db = _DbStat(_SQL_NUMBER_OF_CONNECTIONS)
