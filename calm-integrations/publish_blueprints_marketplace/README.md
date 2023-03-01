# Plublish blueprint to marketplace without substrate spec

## How do we execute this?
You can execute this as a native python script, or as a runbook

## What does this do?
This script publishes existing blueprint to marketplace (LOCAL) within a PC without substrate elements.

## Supported Platforms:
    - VCenter, AHV

## Runbook
1. Import the runbook in Prism Central NCM Self-Service
2. Update the credential for PC
3. Update the variables to match your environment
4. Execute the runbook.
Note - the runbook is executed on your local Calm\PC as an escript.  

## Inputs for publish_blueprints_to_marketplace.py:
* --pc 						- PC Ip address
* --port 					- PC Port
* --user 					- PC Username
* --password 				- PC Password
* --blueprint_name 			- Blueprint name
* -v or --version 			- Version of marketplace blueprint
* -n or --name 				- Name of marketplace Blueprint
* -p or --project 			- Projects for marketplace blueprint (used for approving blueprint)
* -i or --icon	 			- App icon image name to be used (pre-existing only).
* -d or --description 		- Description for marketplace blueprint
* --with_secrets 			- Preserve secrets while publishing blueprints to marketpalce
* --publish_to_marketplace  - Publish the blueprint directly to marketplace skipping the steps to approve, etc.
* --auto_approve			- Auto approves the blueprint
* --existing_markeplace_bp	- Publish as new version of existing marketplace blueprint (Always)

## Example
```
python publish_blueprints_to_marketplace.py --pc 10.0.0.1 --user admin --password xxxxxxxx -v 1.0.1 --name Chef --icon cheficon --description "$(cat ~/Calm/calm-blueprints/Marketplace/Descriptions/1.0.0/Chef.md)" --project regression,default --blueprint_name Chef
```