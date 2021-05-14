docker container inspect my-postgres || docker run --name my-db -e POSTGRES_PASSWORD=postgres123 -p 5432:5432 -d psql-image
docker restart my-postgres