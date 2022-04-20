# Seeding Scripts to the Calm Library

The [Nutanix Calm blueprints repository](https://github.com/nutanix/blueprints) contains hundreds of [Calm team](https://github.com/nutanix/blueprints/tree/master/library/task-library) and [community](https://github.com/nutanix/blueprints/tree/master/task-library) contributed scripts that can be uploaded to the Calm library, under a specified project for access control. These examples can be customized to speed your Calm Blueprint and Runbook development while increasing execute task and variable re-use across a project!

Update 2020-08-25: watch this procedure with Nutanix University's [Calm in Action: Seeding the Task Library](https://www.youtube.com/watch?v=PGBc--1qR_4) video.

Update 2021-01-28: the [Calm DSL](https://github.com/nutanix/calm-dsl/#task-library) client can now manage Calm library resources as well.

## Setup

- Clone the Nutanix Calm blueprints repository: 
    ```shell
    git clone https://github.com/nutanix/blueprints.git
  ```
- Change the directory to: ```calm-integrations/generate_task_library_items```

  ```shell
  cd calm-integrations/generate_task_library_items
  ```

- Assuming you have [Python installed](https://www.python.org/downloads/), prepare your Python virtual environment with the [requests package](https://pypi.org/project/requests/).

    ```shell
  pip install --upgrade pip \
    && pip install --upgrade virtualenv \
    && virtualenv calm \
    && source calm/bin/activate
  ```
  The example below shows the Python virtual environment activated and a shell prompt, so do not copy anything before or including the $
  
    ```shell
  (calm) $ pip install --upgrade requests \
    && ./generate_task_library_items.sh
    ```
- Alternatively, if you have `virtualenv` and [pipenv](https://pipenv.pypa.io/en/latest/) ready:
  ```shell
  pipenv install requests \
    && pipenv run ./generate_task_library_items.sh
  ```

## Environment Variables

To save time, you can export shell environment variables before executing the script by running the following:
  - ```export PC_IP=<Prism Central IP or DNS address>```   
  - ```export PC_USER=<Prism Central user>```
  - ```export PC_PASSWORD=<Prism Central password>```
  - ```export PC_PROJECT=<Prism Central project>```

The Python script assumes Prism Central is on port 9440, you can override the default by setting the `PC_PORT` environment variable to a different port number.

Alternatively, use [direnv](https://direnv.net/) to populate an `.env` file with the above environment variables.

## Procedure

- Execute the script to seed items from the Calm and community contributed directories by running the following command:
  - ```bash generate_task_library_items.sh```
- When prompted, enter the following information (if you have not set environment variables, above):
  - **Prism Central IP:** Enter the Prism Central IP or DNS address to which the library items are to be seeded.
  - **Prism Central User:** Enter the user name with the access to create  library scripts.
  - **Prism Central Password:** Enter the password of the Prism Central user.
  - **Prism Central Project:** Enter the Project name to which the library items can be published.

## Additional Notes

The bash script `generate_task_library_items.sh` prompts for four pieces of information if environment variables are not set or empty. Next, the Calm team and community contributed directories are scanned, searching for files only ending in `.escript`, `.ps1`, `.py`, and `.sh` to allow supporting materials and documentation to remain in the same directory. Finally, the four variables are provided to the Python script `generate_task_library.py` along with the filespec (full directory path and file name) of the resource to be uploaded.

For example, you can seed any **individual resource file** to the Nutanix Calm Library directly:

````shell
python generate_task_library.py \
  --pc $PC_IP --user $PC_USER --password $PC_PASSWORD --project $PC_PROJECT \
  --script <resource file>
````
