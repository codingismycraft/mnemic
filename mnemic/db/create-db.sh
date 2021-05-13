dropdb mnemic;
createdb mnemic;
docker cp ./create-db.sql my-postgres:/
psql mnemic -f /create-db.sql


