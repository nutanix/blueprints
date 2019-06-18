# Bitbucket Sync for Calm Blueprints.

## What does this do?
This scripts connects to your Nutanix Calm instance, iterates over the given list of projects, and for every project, looks at all blueprints in that project. If the blueprint is new, it uploads to bitbucket. If the blueprint is already present in bitbucket, it checks to see if the blueprint has changed/been updated. If changed, it uploads the new blueprint to bitbucket, else skip.
We recommend running this script as a cron job on an hourly/daily cadence to ensure all changes being made to your blueprints are regularly backed up.

### To Dos:
* Backup task library
* Script to upload blueprints/task library items automatically into a blank calm instance

### Source Files
[bitbucket-version-management.py](https://raw.githubusercontent.com/nutanix/blueprints/master/calm-integrations/bitbucket-sync-for-calm-blueprints/bitbucket-sync-for-calm-blueprints.py) script helps to upload blueprints to bitbucket repo.

[config.ini](https://raw.githubusercontent.com/nutanix/blueprints/master/calm-integrations/bitbucket-sync-for-calm-blueprints/config.ini) sample config file.

## Pre-Requisites
* Existing bitbucket account.
	* create a repository in the bitbucket account with directory structure given below (default and project1) are projects in calm.
```.
├── default
│   └── blueprints
│       └── README.md
└── project1
    └── blueprints
        └── README.md
```

* PC VM with calm enabled.
    * CALM v2.6+

## Setup
* Tested on Centos 7.6 & Python version 2.7.13

```mkdir ~/calm-bitbucket-upload && cd ~/calm-bitbucket-upload
virtualenv venv
source venv/bin/activate
pip install requests configparser
```

## Generate config.ini
* Create config.ini file with bitbucket and calm endpoint details in the same directory as the script.

```
[calm]
pc_ip = <pc_ip>
pc_port = <pc_port>
username = <pc_username>
password = <pc_password>
project_list = <project1,project2>
[bitbucket]
owner = <bitbucket_owner>
repository = <bitbucket_repository>
username = <bitbucket_username>
password = <bitbucket_password>
```

## Start backup
```
# (optional) to disable InsecureRequestWarning from python requests
export PYTHONWARNINGS="ignore:Unverified HTTPS request"
# Activate virtual environment
source venv/bin/activate
python bitbucket-version-management.py
```

## Sample Output:
```
(venv) skumar-blr-mbp:bitbucket-bp-upload sarat.kumar$ python bitbucket-version-management.py
Fetching BP AD details.
Updating Bp AD with status code : 201 & message 'Created'.
Fetching BP ghcfg details.
Fetching BP SnortClone details.
Fetching BP Snort details.
Fetching BP eg_400 details.
Fetching BP YFTD-Blueprint-Demo-support details.
Fetching BP LAMPTest details.
```

