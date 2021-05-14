FROM postgres:latest
ENV POSTGRES_PASSWORD=postgres123
ENV POSTGRES_USER=postgres
ENV POSTGRES_DB=mnemic
COPY create-db.sql /docker-entrypoint-initdb.d/create_fixtures.sql
