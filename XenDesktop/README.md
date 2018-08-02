Xendesktop :
==========
XenDesktop is a desktop virtualization software that allows multiple users to access and run Microsoft Windows desktops that are installed at a centralized location separate from the devices from which they are being accessed.
This blueprint create 6 Node Xen Cluster with 2 SQL, 2 DDC and 2 Storefront Node.
Operating System :
------------------
 - Windows Server 2016

Licensing information :
----------------------
 - BYOL

Hypervisor:
-----------
 - Nutanix AHV

Minimum hardware requirement :
-----------------------------
 - 6 GB RAM
 - 4 Core CPU
 - 100 GB Storage

Version:
--------
 - Xen Desktop Version 7.16
 - MSSQL Version 2014 SP2
 - PC version 5.8

Pre-requisites:
---------------
 - An existing Active Directory is required. or [Install Windows Active Directory](https://drive.google.com/open?id=1S0tIOPDTCZKvDWzZnZhyuphPFeGApyjLqUqQWMk2n6s)
 - Windows Server 2016 pre installed image.
 - Download and Push Microsoft SQL server 2014 SP2 iso to PC images.
 - Download and Push Xen App/Desktop 17_16 to PC images.
 - Download Nutanix acropolis plugin for citrix.
 - Setup karan in a windows VM.

Global Variables
----------------
 - DOMAIN - (Domain of the Active directory)
 - AD_IP - (Active directory IP)
 - PE_IP - (PE ip used for creating volume group & nutanix resource)
 - PE_DATA_SERVICE_IP - (optional filer url of Windows Resource Kit Tools 2003)
 - Nutanix_Container_Name - (Nutanix storage container name)
 - Volume_GroupName - (Volume group name)
 - FAILOVER_CLUSTER_NAME - (Failover cluster name)
 - SQL_CLUSTER_NAME - (MSSQL Listener name)
 - FAILOVER_VIP - (Failover cluster static ip)
 - MSSQL_VIP - (MSSQL listener static IP)
 - NutanixAcropolisPlugin - (Acropolis plugin filer url)
 - NutanixAcropolis_Installed_Path - (Install path of Acropolis plugin)
 - XD_SITE_NAME - (DDC site name)
 - CVM_NETWORK - (Network name to create vdi images)
 - BPG_RKTOOLS_URL - (filer url of Windows Resource Kit Tools 2003)

Steps to Deploy:
----------------
 - Upload the Blueprint.
 - Select Windows 2016 image & SQL 2014 Iso for MSSQL, Select Windows 2016 image & Xen App/Desktop iso for DDC and Storefront Calm Services.
 - Set all the required variables.
 - Fill the credentials.
    * LOCAL (Local Creds used before joining to domain)
    * DOMAIN_CRED (Domain creds used to join domain and install tasks)
    * SQL_CRED (Domain creds used by sql to run service as)
    * KARAN_CRED (Karan Creds)
    * PE_CRED (PE creds)
 - Launch BP.

What's inside MSSQL BPG?
------------------------
 - 8 vDisks 
  * SQLINSTALL  - 50GB
  * SQLBCK      - 150GB
  * DATA01      - 300GB
  * DATA02      - 300GB
  * TEMPDB01        - 100GB
  * TEMPDB02        - 100GB
  * TEMPDBLOG01 - 200GB
  * ULOG01      - 200GB

What's next?
------------
 - Create windows client/server image, attach XEN app/desktop iso.
 - Change DNS IP to AD IP. Install VDA agent. And shutdown the vm.
 - Take a snapshot of the VM.
 - Create a machine catalog by selecting above created snapshot.
 - Create a delivery group using the above machine catalog.
 - For more details please take a look at below video
 
 [Video Part1](https://drive.google.com/open?id=1c14tWHCV8efb5GdWhOM7Jnm0tSZ1QqPb)
 [Video Part2](https://drive.google.com/open?id=1SzahZMeTUT84bbiWZuZYs3uVWvuBFSmn)
