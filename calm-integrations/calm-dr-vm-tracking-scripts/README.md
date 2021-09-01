# Script to track DR Failover of UVM from PC -> PC and relink Calm Apps

This script helps customers to relink Calm App to UVM in DR site or vice-versa.

## Pre-requisites:
* Calm 3.x

- `pre-migration-script.py` Script takes 'DEST_PC_IP', 'DEST_PC_USER', 'DEST_PC_PASS' & 'SOURCE_PROJECT_NAME' variables exported as env variables to recreate categories at DR site.
- `post-migration-script.py` Script takes 'DEST_PC_IP', 'DEST_PC_USER', 'DEST_PC_PASS' & 'DEST_PROJECT_NAME' variables exported to re-link Apps with Failover VM's and update APP's project.

## Inputs
* export DEST_PROJECT_NAME="<DEST_PROJECT_NAME>"
* export DEST_PC_IP="<PC_IP>"
* export DEST_PC_USER="<PC_USERNAME>"
* export DEST_PC_PASS="<PC_PASSWORD>"
* export SOURCE_PROJECT_NAME="<SOURCE_PROJECT_NAME>"

## Steps to execute
```shell
# SSH to Calm PC VM
# Docker exec to nucalm container
docker exec -it nucalm bash
cd /tmp
activate

# Copy both the files 'pre-migration-script.py' & 'post-migration-script.py'

# export required variables
export DEST_PROJECT_NAME="<DEST_PROJECT_NAME>"
export DEST_PC_IP="<PC_IP>"
export DEST_PC_USER="<PC_USERNAME>"
export DEST_PC_PASS="<PC_PASSWORD>"
export SOURCE_PROJECT_NAME="<SOURCE_PROJECT_NAME>"

python pre-migration-script.py
python post-migration-script.py
```