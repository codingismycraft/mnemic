"""Exposes constants."""

SQL_INSERT_RUN = """
INSERT INTO tracing_run (uuid, app_name, column_names)  VALUES($1, $2, $3);
"""

SQL_INSERT_ROW = """
INSERT INTO tracing_row (uuid, row_data) VALUES($1, $2);
"""

SQL_SELECT_NUMBER_OF_COLS = """
SELECT CARDINALITY(column_names) AS col_count, uuid 
FROM tracing_run WHERE uuid=$1
"""

SQL_SELECT_COL_NAMES = """
select unnest as col_name, ordinality -1 as index 
from unnest((select column_names from tracing_run where uuid=$1)) 
with ordinality
"""

SQL_SELECT_LATEST_RUN = """
select uuid from tracing_run where app_name=$1 
order by creation_time desc limit 1
"""
