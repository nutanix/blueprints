
Active Directory :
=================
Active Directory (AD) is a Windows OS directory service that facilitates working with interconnected, complex and different network resources in a unified manner.
Active Directory provides a common interface for organizing and maintaining information related to resources connected to a variety of network directories.
The directories may be systems-based (like Windows OS), application-specific or network resources, like printers.
Active Directory serves as a single data store for quick data access to all users and controls access to users based on the directory's security policy.

Operating System :
-----------------
 - Windows Server 2012
 - Windows Server 2012 R2
 - Windows Server 2016

Licensing information :
---------------------
 - BYOL

Hypervisor:
----------
 - VMware Esxi
 - Nutanix AHV

Minimum hardware requirement :
----------------------------
 - 2 GB RAM
 - 2 Core CPU
 - 50 GB Storage

Global Variables
----------------
- `DOMAIN` - Mandatory - Domain name.
- `VMNAME` - Mandatory - Hostname name/ VM name of the server.
- `DOMAIN_TYPE` - Mandatory - Type of domain controller AD, ADC, CDC or RODC.
- `ADMIN_USER` - Mandatory - Administrator username default is administrator.
- `ADMIN_PASSWORD` - Mandatory - Adminstrator user password for remote logins.
- `SERVER` - Optional - IP or Name of Domain controller required in case of CDC, ADC and RODC.
- `CHILD_DOMAIN` - Optional - Child domain name. Mandatory only in-case of CDC.