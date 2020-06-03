#!/bin/bash

## Variable Initialization
IS_SCALEOUT="@@{IS_SCALEOUT}@@" 
PROFILE="@@{PROFILE}@@"
AHV_MASTER_IP="@@{AHVMaster.address}@@"
AWS_MASTER_IP="@@{AWSMaster.address}@@"
GCP_MASTER_IP="@@{GCPMaster.address}@@"
AZURE_MASTER_IP="@@{AzureMaster.address}@@"
VMWARE_MASTER_IP="@@{VMwareMaster.address}@@"
DB_PASSWORD="@@{DB_PASSWORD}@@"

## Check if scaleout action is triggered
if [ ${IS_SCALEOUT:-"NO"} = "YES" ]
then
	exit 0;
fi

## Getting slave ip address 
if [ "x${PROFILE}" = "xAHV" ]
then
    Master_IP="$AHV_MASTER_IP"
elif [ "x${PROFILE}" = "xAWS" ]
then
    Master_IP="$AWS_MASTER_IP"
elif [ "x${PROFILE}" = "xGCP" ]
then
    Master_IP="$GCP_MASTER_IP"    
elif [ "x${PROFILE}" = "xAZURE" ]
then
    Master_IP="$AZURE_MASTER_IP"    
elif [ "x${PROFILE}" = "xVMWARE" ]
then
    Master_IP="$VMWARE_MASTER_IP"     
fi

## Initiating postgres db backup from master
sudo su - postgres <<EOF
  mv 9.6/data 9.6/data.org
  echo "${Master_IP}:5432:*:rep:@@{DB_PASSWORD}@@" > ~/.pgpass
  chmod 0600 ~/.pgpass
  pg_basebackup -h ${Master_IP} -D /var/lib/pgsql/9.6/data -U rep -v -P
EOF

## Update the systemd config postgres
sudo sed -i -e 's/ExecStart=.*/ExecStart=\/usr\/pgsql-9\.6\/bin\/pg_ctl start -D ${PGDATA} -s -W -t 300/g' /usr/lib/systemd/system/postgresql-9.6.service

## Setup a replication user access on slave
echo "host    replication     rep     ${Master_IP}/32     md5" | sudo tee -a /var/lib/pgsql/9.6/data/pg_hba.conf

## Update the slave config as hot standby for replication
echo "listen_addresses = '*'
wal_level = 'hot_standby'
archive_mode = on
archive_command = 'cd .'
max_wal_senders = 3
hot_standby = on
wal_keep_segments = 8" | sudo tee -a /var/lib/pgsql/9.6/data/postgresql.conf

## Create recovery conf for initial change
sudo su - postgres sh -c "touch 9.6/data/recovery.conf"
echo "standby_mode = 'on'
primary_conninfo = 'host=${Master_IP} port=5432 user=rep password=@@{DB_PASSWORD}@@'
trigger_file = '/tmp/postgresql.trigger.5432'" | sudo tee -a /var/lib/pgsql/9.6/data/recovery.conf

## Reload systemd for updated postgresql service and restart the service
sudo systemctl daemon-reload
sleep 2;
sudo systemctl restart postgresql-9.6
sleep 2;
