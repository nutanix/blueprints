#!/usr/bin/env bash

##############################################
# Usage: bash generate_task_library_items.sh #
##############################################

export PYTHONWARNINGS="ignore:Unverified HTTPS request"
IFS=$(echo -en "\n\b")

# shellcheck disable=SC2153
if [[ -z ${PC_IP} ]]; then
  read -p -r "Enter Prism Central IP: " PC_IP
fi
# shellcheck disable=SC2153
if [[ -z ${PC_USER} ]]; then
  read -p -r "Enter Prism Central User: " PC_USER
fi
# shellcheck disable=SC2153
if [[ -z ${PC_PASSWORD} ]]; then
  read -p -r -s "Enter Prism Central Password: " PC_PASSWORD
  # using "-s" stops BASH from displaying \n after enter password
  echo "" # echo blank line to cleanup terminal
fi
# shellcheck disable=SC2153
if [[ -z ${PC_PROJECT} ]]; then
  read -p -r "Enter Prism Central Project: " PC_PROJECT
fi

echo "Counting resources and seeding to ${PC_IP}..."

for source_directory in ../../library/task-library ../../task-library; do
  count=0 # reset

  case "${source_directory}" in
    '../../library/task-library')
      source_type='Nutanix Calm'
      ;;
    '../../task-library')
      source_type='community'
      ;;
  esac

  SCRIPT_COUNT=$(find "${source_directory}" \
    -type f \( -name "*.escript" \
    -o -name "*.ps1" \
    -o -name "*.py" \
    -o -name "*.sh" \) -print \
    | wc | awk '{print $1}') \
    && echo -e "\nFound ${SCRIPT_COUNT} items in ${source_type:-unknown type}" \
      " directory: ${source_directory}\n" \
    && while IFS= read -r -d '' item; do
      ((count++))
      echo "- ${count} of ${SCRIPT_COUNT} ($((count * 100 / SCRIPT_COUNT))%): $(basename "${item}")"
      python generate_task_library.py --script "${item}" \
        --pc "${PC_IP}" --user "${PC_USER}" --password "${PC_PASSWORD}" --project "${PC_PROJECT}"
    done < <(find "${source_directory}" \
      -type f \( -name "*.escript" \
      -o -name "*.ps1" \
      -o -name "*.py" \
      -o -name "*.sh" \) -print0)
done
