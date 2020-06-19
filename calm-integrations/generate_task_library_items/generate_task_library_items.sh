#!/bin/bash

##############################################
# Usage: bash generate_task_library_items.sh #
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
   # echo blank line to cleanup terminal
   # using "-s" stops BASH from displaying \n after enter password
   echo ""
else
   pc_password=${PC_PASSWORD}
fi
if [[ -z "${PC_PROJECT}" ]]; then
   read -p "Enter Prism Central Project: " pc_project
else
   pc_project=${PC_PROJECT}
fi

# grab some info about how many scripts will be imported
# not mandatory but just gives the user an idea of how much there is to do
PUBLISHED_SCRIPT_COUNT=`find  ../../library/task-library -type f -print | wc | awk '{print $1}'`
COMMUNITY_SCRIPT_COUNT=`find  ../../task-library -type f \( -name "*.ps1" -o -name "*.sh" -o -name "*.py" \) -print | wc | awk '{print $1}'`

#Seed nutanix calm published scripts
echo "$PUBLISHED_SCRIPT_COUNT published scripts to import."
for items in `find  ../../library/task-library -type f -print` ; do
    python generate_task_library.py --pc $pc_ip --user $pc_user --password $pc_password --project $pc_project --script $items
done

#Seed community published scripts
echo "$COMMUNITY_SCRIPT_COUNT community scripts to import."
for items in `find  ../../task-library -type f \( -name "*.ps1" -o -name "*.sh" -o -name "*.py" \) -print` ; do
    python generate_task_library.py --pc $pc_ip --user $pc_user --password $pc_password --project $pc_project --script $items
done
