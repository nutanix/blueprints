# SEEDING SCRIPTS TO THE CALM TASK LIBRARY
Calm published blueprints repository contains scripts that can be seeded into task library and published to projects.We can use these tasks for blueprint configuration.Perform the following procedure to seed task library items to Nutanix Calm.

## Procedure
- Clone the blueprints repository from github. 
- To access the repository, [Click here](https://github.com/nutanix/blueprints/).
- Change the directory to ```calm-integrations/generate_task_library_items```
- We can execute the script to seed by running the following command in bash.
- ```bash generate_task_library_items.sh```
- When prompted, enter the following information.
  - **Prism Central IP:** Enter the Prism Central IP address to which the task library items are to be seeded.
  - **Prism Central User:** Enter the user name with the access to create task library scripts.
  - **Prism Central Password:** Enter the password of the Prism Central user.
  - **Prism Central Project:** Enter the Project name to which the task library items can be published.
  
**Optionally**, to avoid giving inputs multiple time, you can also export environment variables before running the script by running the following command.
  - ```export PC_IP=<prism central IP>```   
  - ```export PC_USER=<prism central user>```
  - ```export PC_PASSWORD=<prism central password>```
  - ```export PC_PROJECT=<prism central project>```
  
Also, we can seed **individual files** into Nutanix Calm by running the following Python script.

```python generate_task_library.py --pc $PC_IP--user $PC_USER --password $PC_PASSOWORD --project $PC_PROJECT --script <path of script file>```
