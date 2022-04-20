# Commvault integration

## Application Profile variables

* **CommvaultBackupGetVMGroups.py**. This variable lists to the user the Commvault VM Groups available. Create Escript variable with the name *CV_VM_GROUP*. Make sure to create all the variables this script depends upon.

## Package Install tasks

* **CommvaultBackupAddVMtoGroup.py**. This task adds the VM into the Commvault VM Group seleted by the user during launch. Create Escript execution task. Make sure to create the credential this script depends upon. This script makes use of *CV_VM_GROUP* application profile variable.

* **CommvaultBackupRunSubclientBackup.py**. This task runs a backup job for the Commvault VM Group seleted by the user during launch. Create Escript execution task. Make sure this task goes after *CommvaultBackupAddVMtoGroup.py*. This script makes use of *CV_VM_GROUP* application profile variable.

## Package Uninstall tasks

* **CommvaultBackupRemoveVMfromGroup.py**. This task removes the VM from the Commvault VM Group seleted by the user during launch. Create Escript execution task. This script makes use of *CV_VM_GROUP* application profile variable.
