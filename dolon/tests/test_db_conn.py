"""Tests the db_conn module."""

import os
import unittest

import dolon.db_conn as db_conn
import dolon.exceptions as exceptions

# Aliases.
DbConnection = db_conn.DbConnection


class DbConnectionTest(unittest.TestCase):
    """Tests the DbConnection class."""

    def test_invalid_environment(self):
        """Tests invalid environment."""
        if "POSTGRES_CONN_STR" in os.environ:
            del os.environ["POSTGRES_CONN_STR"]
        with self.assertRaises(exceptions.InvalidEnvironmentVariable):
            DbConnection._get_conn_str()

    def test_get_conn_str(self):
        """Tests the get_conn_str method."""
        conn_str = 'postgresql://postgres:postgres123@localhost:5432/mnemic'
        os.environ["POSTGRES_CONN_STR"] = conn_str
        self.assertEqual(conn_str, DbConnection._get_conn_str())


if __name__ == '__main__':
    unittest.main()
