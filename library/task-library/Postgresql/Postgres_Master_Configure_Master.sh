#!/bin/bash

## Variable Initialization
PROFILE="@@{PROFILE}@@"
AHV_SLAVE_IPS="@@{AHVSlave.address}@@"
AWS_SLAVE_IPS="@@{AWSSlave.address}@@"
GCP_SLAVE_IPS="@@{GCPSlave.address}@@"
AZURE_SLAVE_IPS="@@{AzureSlave.address}@@"
VMWARE_SLAVE_IPS="@@{VMwareSlave.address}@@"
MASTER_IP="@@{address}@@"
DB_PASSWORD="@@{DB_PASSWORD}@@"

## Getting slave ip address 
if [ "x${PROFILE}" = "xAHV" ]
then
    Slaves=($(echo "${AHV_SLAVE_IPS}" | sed 's/^,//' | sed 's/,$//' | tr "," " ")) 
elif [ "x${PROFILE}" = "xAWS" ]
then
    Slaves=($(echo "${AWS_SLAVE_IPS}" | sed 's/^,//' | sed 's/,$//' | tr "," " ")) 
elif [ "x${PROFILE}" = "xGCP" ]
then
    Slaves=($(echo "${GCP_SLAVE_IPS}" | sed 's/^,//' | sed 's/,$//' | tr "," " "))     
elif [ "x${PROFILE}" = "xAZURE" ]
then
    Slaves=($(echo "${AZURE_SLAVE_IPS}" | sed 's/^,//' | sed 's/,$//' | tr "," " "))     
elif [ "x${PROFILE}" = "xVMWARE" ]
then
    Slaves=($(echo "${VMWARE_SLAVE_IPS}" | sed 's/^,//' | sed 's/,$//' | tr "," " "))     
fi

## Creating an user for replication
sudo -i -u postgres psql -c "CREATE USER rep REPLICATION LOGIN ENCRYPTED PASSWORD '${DB_PASSWORD}'; "

## Configuring access for each slave
echo "host    replication     rep     ${MASTER_IP}/32     md5" | sudo tee -a /var/lib/pgsql/9.6/data/pg_hba.conf
for slave in ${Slaves[@]} 
do
  echo "host    replication     rep     ${slave}/32     md5" | sudo tee -a /var/lib/pgsql/9.6/data/pg_hba.conf
done

## Creating db instance as Master
echo "listen_addresses = '*'
wal_level = 'hot_standby'
archive_mode = on
archive_command = 'cd .'
max_wal_senders = 3
hot_standby = on
wal_keep_segments = 8" | sudo tee -a /var/lib/pgsql/9.6/data/postgresql.conf 


sudo systemctl restart postgresql-9.6 

## This sleep is important to make sure Postgres is restarted successfully and device is not busy
sleep 10;
