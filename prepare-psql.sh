docker container inspect my-postgres || docker run --name my-postgres -e POSTGRES_PASSWORD=postgres123 -d postgres
docker restart my-postgres
alias psql='docker exec -it my-postgres psql -U postgres'
alias dropdb='docker exec -it my-postgres dropdb -U postgres'
alias createdb='docker exec -it my-postgres createdb -U postgres'
