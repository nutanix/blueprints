#!/bin/bash

cd /tmp

## Create icinga db user
sudo -u postgres psql -c "CREATE ROLE icinga WITH LOGIN PASSWORD 'icinga'"
sudo -u postgres createdb -O icinga -E UTF8 icinga

## Create icingaweb2 db user
sudo -u postgres psql -c "CREATE ROLE icingaweb2 WITH LOGIN PASSWORD 'icingaweb2'"
sudo -u postgres createdb -O icingaweb2 -E UTF8 icingaweb2

## Configure db user access for Icinga DB
echo "# icinga
local   icinga      icinga                            md5
host    icinga      icinga      127.0.0.1/32          md5
host    icinga      icinga      ::1/128               md5

local   icingaweb2      icingaweb2                            md5
host    icingaweb2      icingaweb2      127.0.0.1/32          md5
host    icingaweb2      icingaweb2      ::1/128               md5

# local is for Unix domain socket connections only
local   all         all                               ident
# IPv4 local connections:
host    all         all         127.0.0.1/32          ident
# IPv6 local connections:
host    all         all         ::1/128               ident" | sudo tee /var/lib/pgsql/data/pg_hba.conf

## Restart DB Service
sudo systemctl restart postgresql
sleep 2

## Create Icinga Schema
export PGPASSWORD=icinga
psql -U icinga -d icinga < /usr/share/icinga2-ido-pgsql/schema/pgsql.sql


## Create IcingaIDOConnection object
echo "object IdoPgsqlConnection \"ido-pgsql\" {
  user = \"icinga\"
  password = \"icinga\"
  host = \"localhost\"
  database = \"icinga\"
}" | sudo tee /etc/icinga2/features-available/ido-pgsql.conf

## Enable icinga ido-pgsql
sudo icinga2 feature enable ido-pgsql

## Restarting Icinga
sudo systemctl restart icinga2


