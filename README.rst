Changelog
=========

- 2018.09.17: Complete resdesign of both Ansible and SaltStack blueprints
- 2018.09.17: v2 of SaltStack Website uploaded.  Complete redesign of app.
- 2018.09.12: Migrated all blueprints from old "Automation" repo to https://github.com/nutanix/blueprints (this repo)

Blueprints
==========

Please following the instructions below to push to this repo:
  * Create a separate directory. The name of the directory and the blueprint name should be same.
  * Should have a README.md file and have the following informations:
      * Mention the PC build version on which the particular blueprint was created and tested.
      * Mention the prerequisites details like:
          * Minimum Harware required
          * Operating System Versions   
      * Variables required to run the blueprints. 
      * Credentials information.
      * Platform information like AHV, AWS, GCP, vCenter, Azure, etc.
      * Minimum and Maximum number of VMs
      * Actions like ScaleUp and ScaleDown
      * Custom actions informations. 
      * License information.
      * Network information.
      * Disks information.
