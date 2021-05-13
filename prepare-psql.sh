docker container inspect my-postgres || docker run --name my-postgres -e POSTGRES_PASSWORD=postgres123 -p 5432:5432 -d postgres
docker restart my-postgres