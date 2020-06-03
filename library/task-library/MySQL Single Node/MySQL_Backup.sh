#!/bin/bash

### Setup variables
mysql_password="@@{DB_PASSWORD}@@"
date_part=`date +%F`
mkdir -p @@{BACKUP_FILE_PATH}@@
sudo mysqldump -u root -p${mysql_password} --all-databases | sudo gzip -9 > @@{BACKUP_FILE_PATH}@@/db_dump.sql.gz