#!/bin/bash
set -ex

# -*- Setup variables
mysql_password="@@{MYSQL_PASSWORD}@@"
server_id=`sudo cat /etc/my.cnf.d/nutanix.cnf | grep  "server-id=" | cut -d= -f2`
is_master=`sudo cat /etc/my.cnf.d/nutanix.cnf | grep -q -w "#master=$server_id"; echo $?`

## -*- Run only on master
if [ ${is_master} -eq 0 ]
then
sudo sed -i "/\[mysqld\]/a innodb_flush_log_at_trx_commit=1" /etc/my.cnf.d/nutanix.cnf
sudo sed -i "/\[mysqld\]/a sync_binlog=1" /etc/my.cnf.d/nutanix.cnf

## -*- Create Replica User and grant the permission for all slaves
sudo mysql -u root -p${mysql_password}<<EOF
CREATE USER 'replica'@'%' IDENTIFIED BY "${mysql_password}";
GRANT REPLICATION SLAVE ON *.* to replica@'%';
FLUSH PRIVILEGES;
EOF
fi

##  -*- Restart MySQL service for changes to take effect
sudo touch /var/run/mysqld/mysqld.sock
sudo chown mysql:mysql /var/run/mysqld/mysqld.sock
sudo systemctl restart mysqld

sleep 5

if [ ${is_master} -eq 0 ]
then
    ## Wait for master to get into running status
    while true
    do
      status=`sudo systemctl status mysqld | grep Active: | awk ' { print $3 }' | sed 's#[(|)]##g'`
  	  [ $status = "running" ] && break
      echo $status
  	  sleep 2
    done
    
    ## Get MySQL bin log and position details
    MYSQL_BIN=$(sudo mysql -u root -p${mysql_password} -e 'show master status;' | grep mysql-bin | awk '{print $1}')
	MYSQL_POSITION=$(sudo mysql -u root -p${mysql_password} -e 'show master status;' | grep mysql-bin | awk '{print $2}')
    
  ## Evaluates MYSQL_BIN and MYSQL_POSITION vars
  echo "MYSQL_BIN=$MYSQL_BIN"
  echo "MYSQL_POSITION=$MYSQL_POSITION"
fi

## -*- Enable and start the mysqld process
sudo systemctl enable mysqld
sudo systemctl start mysqld
sudo systemctl status mysqld