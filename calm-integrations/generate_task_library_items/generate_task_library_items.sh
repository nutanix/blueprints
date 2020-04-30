#!/bin/bash

export PYTHONWARNINGS="ignore:Unverified HTTPS request"

for items in `ls $(pwd)/../` ; do
    python generate_task_library.py $(pwd)/../${items}
done
