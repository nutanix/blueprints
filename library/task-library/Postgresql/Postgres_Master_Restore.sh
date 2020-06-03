#!/bin/bash

db_name="@@{DB_NAME}@@"
restore_file_path="@@{RESTORE_FILE_PATH}@@"

sudo su - postgres bash -c "gunzip -c ${restore_file_path} | psql ${db_name}"