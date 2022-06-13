# Apply vm-host affinity policy during a VM deployment or update post deployment from CALM app.

This section of the blueprints repo demonstrates how to better leverage host affinities for VM deployment and management from Calm. Initially we providing a sample blueprint (Host_Affinity_Update.json) that would deploy a new Centos 
VM, also has a custom action built in order to change the VM host affinity to other hosts as day 2 operation.

Here is the overview from the profile action:
![conceptual overview](/host-affinity/blob/change-vm-host-affinity-action.png?raw=true)

## Breakdown of the node blueprint actions:

 Once the action is run, it will prompt following and ask for new desired hosts list:
 ![conceptual overview](/host-affinity/blob/change-ation-prompt.png?raw=true)

 The action has the following 3 main sections. First task collects the hostnames and publishes it for the successive service actions:

  - Delete Affinity Policy: This is a service action that comprised of few tasks that auto collects exiting host names, deletes the associated affinity, waits a little to sync and then deletes the host and category association that it originally created.
![conceptual overview](/host-affinity/blob/delete-existing-affinity?raw=true)

  - Replace New Affinity Policy: This service action does pretty much everything in reverse what the previous action did. It first reestablishes the category association with the new hosts. Then creates the same affinity with the VM category and new hosts category, waits a little to sync up, check for availability of newly created affinity policy, then finally republishes the host names for the sanity of the workflow and successive use. that comprised of few tasks that auto collects exiting host names, deletes the associated affinity, waits a little to sync and then deletes the host and category association that it originally created.
![conceptual overview](/host-affinity/blob/set-new-affinity?raw=true)

 This talks leverages AOS 6.1 api for [host affinities](https://portal.nutanix.com/page/documents/details?targetId=AHV-Admin-Guide-v6_1:ahv-affinity-policies.html) that would also require Calm 3.5+ and Prism Central PC2022.1.02+
