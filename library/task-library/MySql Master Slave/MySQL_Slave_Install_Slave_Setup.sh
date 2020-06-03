#!/bin/bash
set -ex

## -*- Variable Initialization
HOSTNAME="@@{name}@@"

## -*- Setup hostname 
sudo hostnamectl set-hostname ${HOSTNAME}

## -*- Mysql installation 
sudo yum install -y --quiet "http://repo.mysql.com/mysql80-community-release-el7.rpm"
sudo yum update -y --quiet
sudo yum install -y --quiet sshpass mysql-community-server.x86_64

## -*- Mysql config 
echo "!includedir /etc/my.cnf.d" | sudo tee -a /etc/my.cnf
echo "[mysqld]
binlog-format=mixed
log-bin=mysql-bin
datadir=/mysql/data
default_authentication_plugin=mysql_native_password
sql_mode=NO_ENGINE_SUBSTITUTION,STRICT_TRANS_TABLES
innodb_data_home_dir = /mysql/data
innodb_log_group_home_dir = /mysql/log
innodb_file_per_table
tmpdir=/mysql/tmpdir
innodb_undo_directory = /mysql/undo
default-storage-engine = innodb
default_tmp_storage_engine = innodb
innodb_log_files_in_group = 4
innodb_log_file_size = 1G
innodb_log_buffer_size = 8M
innodb_buffer_pool_size = 6G	
large-pages	
innodb_buffer_pool_instances = 64	
innodb_flush_method=O_DIRECT	
innodb_flush_neighbors=0	 
innodb_flush_log_at_trx_commit=1
innodb_buffer_pool_dump_at_shutdown=1	
innodb_buffer_pool_load_at_startup=1	
bulk_insert_buffer_size = 256	
innodb_thread_concurrency = 16	
 	 
# Undo tablespace	 
innodb_undo_tablespaces = 5	
 	 
# Networking	 
wait_timeout=57600	 
max_allowed_packet=1G	
socket=/var/lib/mysql/mysql.sock	 
skip-name-resolve
port=3306	
max_connections=1000	


[mysqld_safe]
log-error=/mysql/log/mysqld.log
pid-file=/var/run/mysqld/mysqld.pid" | sudo tee /etc/my.cnf.d/nutanix.cnf

## Update the mysql conf for slave
sudo sed -i '/\[mysqld\]/a read_only=1' /etc/my.cnf.d/nutanix.cnf


## -*- Modify Sysctl configuration
mysql_grp_id=`id -g mysql`
sudo sysctl -w vm.swappiness=0
sudo sysctl -w vm.nr_hugepages=1024
sudo sysctl -w vm.overcommit_memory=1
sudo sysctl -w vm.dirty_background_ratio=5 
sudo sysctl -w vm.dirty_ratio=15
sudo sysctl -w vm.dirty_expire_centisecs=500
sudo sysctl -w vm.dirty_writeback_centisecs=100
sudo sysctl -w vm.hugetlb_shm_group=$mysql_grp_id

echo "vm.swappiness=0
vm.nr_hugepages=1024
vm.overcommit_memory=1
vm.dirty_background_ratio=5 
vm.dirty_ratio=15
vm.dirty_expire_centisecs=500
vm.dirty_writeback_centisecs=100
vm.hugetlb_shm_group=$mysql_grp_id" | sudo tee  -a /etc/sysctl.conf

echo "ACTION=='add|change', SUBSYSTEM=='block', RUN+='/bin/sh -c \"/bin/echo 1024 > /sys%p/queue/max_sectors_kb\"'" | sudo tee /etc/udev/rules.d/71-block-max-sectors.rules

## -*- Mount the partition and change the permissions
echo "/dev/mysqlDataVG/mysqlDataLV /mysql/data ext4 rw,seclabel,noatime,nobarrier,stripe=4096,data=ordered 0 0" | sudo tee -a /etc/fstab
echo "/dev/mysqlLogVG/mysqlLogLV /mysql/log ext4 rw,seclabel,noatime,nobarrier,stripe=4096,data=ordered 0 0" | sudo tee -a /etc/fstab
sudo mkdir -p /mysql/log /mysql/data /mysql/tmpdir /mysql/undo
sudo mount -a
sudo chown -R mysql:mysql /mysql

## -*- Enable systemctl service and cleanup data file if any
sudo systemctl enable mysqld
sudo rm -rf /mysql/data/*
sudo systemctl start mysqld
sleep 2

## Fix to obtain temp password and set it to blank
password=$(sudo grep -oP 'temporary password(.*): \K(\S+)' /var/log/mysqld.log)
sudo mysqladmin --user=root --password="$password" password aaBB**cc1122
sudo mysql --user=root --password=aaBB**cc1122 -e "UNINSTALL COMPONENT 'file://component_validate_password'"
sudo mysqladmin --user=root --password="aaBB**cc1122" password ""


## MySQL secure installation
sudo mysql -u root<<-EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY '@@{MYSQL_PASSWORD}@@';
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
DELETE FROM mysql.user WHERE User='';
DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%';
FLUSH PRIVILEGES;
EOF

