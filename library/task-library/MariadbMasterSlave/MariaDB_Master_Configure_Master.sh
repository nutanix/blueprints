#!/bin/bash -xe

# Configure master to enable replication
sudo sed -i "/\[mysqld\]/a innodb_flush_log_at_trx_commit=1" /etc/my.cnf.d/nutanix.cnf
sudo sed -i "/\[mysqld\]/a sync_binlog=1" /etc/my.cnf.d/nutanix.cnf

sudo mysql -u root -p'@@{AHV_Mariadb_Master.MARIADB_PASSWORD}@@' -e "
grant replication slave on *.* TO slave@'%' identified by '@@{AHV_Mariadb_Master.MARIADB_PASSWORD}@@'"

# Restart service after replication config
sudo systemctl restart mysqld

# Fetch master status
STATE=`mysql -u root -p'@@{AHV_Mariadb_Master.MARIADB_PASSWORD}@@' -e 'show master status'`

echo BINLOG_FILE=`echo "$STATE" | awk 'END {print $1}'`
echo BINLOG_POSITION=`echo "$STATE" | awk 'END {print $2}'`
