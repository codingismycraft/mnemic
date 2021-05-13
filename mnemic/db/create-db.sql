
CREATE TABLE tracing_run (
     id serial PRIMARY KEY,
     uuid VARCHAR UNIQUE NOT NULL,
     app_name VARCHAR (128) NOT NULL,
     column_names text[],
     creation_time  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     unique(uuid, app_name)
);

CREATE TABLE tracing_row
(
    id serial PRIMARY KEY,
    uuid VARCHAR,
    row_data real[],
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

