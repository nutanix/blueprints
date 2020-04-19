#!/bin/bash -xe

# Slave config with master status
mysql -u root -p'@@{MariaDB_Master.MARIADB_PASSWORD}@@' -e "
CHANGE MASTER TO MASTER_HOST='@@{MariaDB_Master.address}@@',MASTER_USER='slave', MASTER_PASSWORD='@@{MariaDB_Master.MARIADB_PASSWORD}@@', MASTER_LOG_FILE='@@{MariaDB_Master.BINLOG_FILE}@@', MASTER_LOG_POS=@@{MariaDB_Master.BINLOG_POSITION}@@;
start slave;
show slave status\G
"
