#!/bin/bash

## -*- Setup variables
mysql_password="@@{MYSQL_PASSWORD}@@"
master_ip="@@{MySQL_Master.address}@@"
master_bin="@@{MySQL_Master.MYSQL_BIN}@@"
master_position="@@{MySQL_Master.MYSQL_POSITION}@@"

server_id=`sudo cat /etc/my.cnf.d/nutanix.cnf | grep  "server-id=" | cut -d= -f2`
is_master=`sudo cat /etc/my.cnf.d/nutanix.cnf | grep -q -w "#master=$server_id"; echo $?`

## -*- Runs on slaves and initiates replication
if [ ${is_master} -ne 0 ]
then
  sudo mysql -u root -p${mysql_password} -e "change master to master_host='${master_ip}',master_user='replica',master_password='${mysql_password}',master_log_file='${master_bin}',master_log_pos=${master_position};"
  sudo mysql -u root -p${mysql_password} -e 'start slave;'
  sudo mysql -u root -p${mysql_password} -e 'show slave status\G' | grep -A11 Slave_IO_State
fi

## -*- Enable and start the mysqld process
sudo systemctl enable mysqld
sudo systemctl start mysqld
sudo systemctl status mysqld
