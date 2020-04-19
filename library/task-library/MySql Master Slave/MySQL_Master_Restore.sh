#!/bin/bash

### Setup variables
mysql_password="@@{DB_PASSWORD}@@"
db_file=@@{RESTORE_FILE_PATH}@@

sudo gunzip < $db_file | sudo mysql -u root -p${mysql_password} 