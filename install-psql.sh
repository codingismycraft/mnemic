sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib
sudo sed -i 's/md5/trust/g' /etc/postgresql/12/main/pg_hba.conf
sudo sed -i 's/peer/trust/g' /etc/postgresql/12/main/pg_hba.conf
sudo /etc/init.d/postgresql restart
sudo -u postgres bash -c "psql -c \"CREATE USER vagrant WITH PASSWORD 'vagrant';\""
sudo -u postgres bash -c "psql -c \"ALTER ROLE vagrant WITH CREATEDB;\""
sudo -u postgres bash -c "psql -c \"alter user vagrant with encrypted password 'test';\""
sudo -u postgres bash -c "psql -c \"ALTER user vagrant WITH SUPERUSER;\""
# See also
# https://stackoverflow.com/questions/18664074/getting-error-peer-authentication-failed-for-user-postgres-when-trying-to-ge
