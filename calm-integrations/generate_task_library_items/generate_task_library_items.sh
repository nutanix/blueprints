#!/bin/bash

##############################################
# Usage: bash generate_task_library_items.sh
##############################################

export PYTHONWARNINGS="ignore:Unverified HTTPS request"
IFS=$(echo -en "\n\b")

if [[ -z "${PC_IP}" ]]; then
   read -p "Enter Prism Central IP: " pc_ip
else
   pc_ip=${PC_IP}
fi
if [[ -z "${PC_USER}" ]]; then
   read -p "Enter Prism Central User: " pc_user
else
   pc_user=${PC_USER}
fi
if [[ -z "${PC_PASSWORD}" ]]; then
   read -s -p "Enter Prism Central Password: " pc_password
else
   pc_password=${PC_PASSWORD}
fi
if [[ -z "${PC_PROJECT}" ]]; then
   read -p "Enter Prism Central Project: " pc_project
else
   pc_project=${PC_PROJECT}
fi

#Seed nutanix calm published scripts
for items in `find  ../../library/task-library -type f -print` ; do
    python generate_task_library.py --pc $pc_ip --user $pc_user --password $pc_password --project $pc_project --script $items
done

#Seed community published scripts
for items in `find  ../../task-library -type f \( -name "*.ps1" -o -name "*.sh" -o -name "*.py" \) -print` ; do
    python generate_task_library.py --pc $pc_ip --user $pc_user --password $pc_password --project $pc_project --script $items
done
