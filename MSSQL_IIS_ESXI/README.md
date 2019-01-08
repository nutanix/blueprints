MS-SQL+IIS :
===============
Microsoft SQL Server is a relational database management system developed by Microsoft. As a database server, it is a software product with the primary function of storing and retrieving data as requested by other software applications.Also we are installing Internet Information Services (IIS, formerly Internet Information Server) is an extensible web server created by Microsoft for use with the Windows NT family.
This blueprint create 1 SQL VM and 2 IIS VM's.

Operating System :
------------------
 - Windows Server 2016
 - Windows Server 2012 R2

Licensing information :
----------------------
 - BYOL

Hypervisor:
-----------
 - VMWare ESXI

Minimum hardware requirement :
-----------------------------
 - Windows Template 

Version:
--------
 - MSSQL Version 2014 SP2
 - Calm Version 2.6.0

Pre-requisites:
---------------
 - An existing Active Directory is required. or [Install Windows Active Directory](https://goo.gl/gMTAsa)
 - Download and Push Microsoft SQL server 2014 SP2 exe file into a windows file share

Global Variables
----------------
 - EXE_SHARE_PATH - (Share path of MSSQL Express exe file)

Steps to Deploy:
----------------
 - Upload the Blueprint.
 - Select Windows 2016/2102 R2 template
 - Set all the required variables.
 - Fill the credentials.
    * DOMAIN_CREDENTIAL (Domain creds used to join domain and install tasks)
 - Launch BP.

