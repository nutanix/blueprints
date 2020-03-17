# main contributor for this folder is: Igor Zecevic (igor.zecevic@nutanix.com)
# code review, testing and documentation: Stéphane Bourdeaud (stephane.bourdeaud@nutanix.com)

The escripts in this folder are in 2 categories: SOAP and REST.
Newer versions of vSphere have a partial REST api.  Anything that cannot be done there is done using the SOAP api.

The SOAP api documentation is available here: https://code.vmware.com/apis/196/vsphere
When accessing it, the url to use is always: https://<vcenter>/sdk/vimService.wsdl
There is a login and a logout function.

The REST api documentation is available here: https://vmware.github.io/vsphere-automation-sdk-rest/vsphere/
When accessing it, the base url is: https://<vcenter>/rest/com/vmware/cis/
There is also a login/logout endpoint (/session)

Typical task workflows include (to be added to the install/uninstall packages of the substrate; note that it is easier to create a custom action on the service with those task workflows, then add the action to the install/uninstall package):

1/ Putting all VMs of a Calm application instance in the same vCenter VM folder (whose name is the same as the Calm app):
    
    Install package workflow:
    a/ VcSoapGetObjects
    b/ VcSoapCreateVmFolder
    c/ Wait for 45 seconds
    d/ VcSoapGetVmFolder
    e/ VcSoapMoveVmFolder (to vc_vm_folder_id)

    Uninstall package workflow:
    a/ VcSoapMoveVmFolder (to vc_vm_folder_root_id)
    b/ Wait for 45 seconds
    c/ VcSoapDeleteFolder

2/ Tagging VMs with the Calm application instance name:

    Install package workflow:
    a/ VcRestCreateTag
    b/ Wait for 45 seconds
    c/ VcRestGetTag
    d/ VcRestTagAssociation (with the 'attach' action)

    Uninstall package workflow:
    a/ VcRestTagAssociation (with the 'detach' action)
    b/ Wait for 45 seconds
    c/ VcRestDeleteTag

3/ Creating and updating VM anti-affinity rules for VMs within the same service of the same Calm application instance:

    Install package workflow:
    a/ VcSoapCreateVmDrsRules
    b/ Wait for 45 seconds
    c/ VcSoapUpdateVmDrsRules (with the 'edit' and 'add' actions)

    Uninstall package workflow
    a/ VcSoapUpdateVmDrsRules (with the 'edit' and 'remove' actions)
    b/ Wait for 45 seconds
    c/ VcSoapDeleteVmDrsRules

Note that all those tasks include login/logout at a task level to avoid session timeout issues and deliver more consistent results.
