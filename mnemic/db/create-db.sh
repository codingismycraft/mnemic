dropdb $1;
createdb $1;
psql $1 -f create-db.sql
sudo -u postgres bash -c "psql -c \"grant all privileges on database mnemic to vagrant;\""
