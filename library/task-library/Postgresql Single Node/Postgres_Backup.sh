#!/bin/bash

db_name="@@{DB_NAME}@@"
backup_file_path="@@{BACKUP_FILE_PATH}@@"

sudo su - postgres bash -c "pg_dump ${db_name} | gzip > ${backup_file_path}"