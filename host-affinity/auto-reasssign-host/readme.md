# Automatically reassign a VM to a host on update

This section talk about how VM could be automatically glued to certain host groups based on its naming convention. This example here has two main components to it one the Prism Pro playbook and another is a runbook.

## Description of the components:
 
![conceptual overview](/host-affinity/auto-reassign-host/images/playbook-structure.png?raw=true)

 - Playbook: The above playbook (Auto Update VM Hosts.json) is hooked with a VM update event. As soon as a VM update happens, the workflow executes and it finds out if the VM is Linux or Windows type and passes that to the runbook in the following.

  - Runbook: The runbook first figures out whether the VM is already on the right host or not, if it is not it picks the first host from the configured host list for that type of OS. Rest of the tasks in the runbook creates both host and vm categories and finally creates an affinity rule bonding these two entities which will put the VM to the appropriate host.

![conceptual overview](/host-affinity/auto-reassign-host/images/runbook.png?raw=true)