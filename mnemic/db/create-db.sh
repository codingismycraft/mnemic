dropdb mnemic;
createdb mnemic;
psql mnemic -f create-db.sql
sudo -u postgres bash -c "psql -c \"grant all privileges on database mnemic to vagrant;\""
