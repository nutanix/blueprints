MS-SQL2014 :
==========
Microsoft SQL Server is a relational database management system developed by Microsoft. As a database server, it is a software product with the primary function of storing and retrieving data as requested by other software applications.
This blueprint create 1 SQL VM.

Operating System :
------------------
 - Windows Server 2016
 - Windows Server 2012 R2

Licensing information :
----------------------
 - BYOL

Hypervisor:
-----------
 - Nutanix AHV

Minimum hardware requirement :
-----------------------------
 - 4 GB RAM
 - 4 Core CPU
 - 100 GB Storage

Version:
--------
 - MSSQL Version 2014 SP2
 - PC version 5.8

Pre-requisites:
---------------
 - An existing Active Directory is required. or [Install Windows Active Directory](https://goo.gl/gMTAsa)
 - Windows Server 2016 pre installed and syspreped.
 - Download and Push Microsoft SQL server 2014 SP2 iso to PC images.
 - [Setup karan in a windows VM](https://goo.gl/s3eQ1S)

Global Variables
----------------
 - DOMAIN - (Domain of the Active directory)
 - AD_IP - (Active directory IP)
 - INCLUDE_BPG - (yes/no flag to include best practices or not)
 - BPG_RKTOOLS_URL - (filer url of Windows Resource Kit Tools 2003)

Steps to Deploy:
----------------
 - Upload the Blueprint.
 - Select Windows 2016 image & SQL 2014 Iso for MSSQL.
 - Set all the required variables.
 - Fill the credentials.
    * LOCAL (Local Creds used before joining to domain)
    * DOMAIN_CRED (Domain creds used to join domain and install tasks)
    * SQL_CRED (Domain creds used by sql to run service as)
    * KARAN_CRED (Karan Creds)
 - Launch BP.

What's inside MSSQL BPG?
------------------------
 - 8 vDisks 
    * SQLINSTALL  - 50GB
    * SQLBCK      - 150GB
    * DATA01      - 300GB
    * DATA02      - 300GB
    * TEMPDB01    - 100GB
    * TEMPDB02    - 100GB
    * TEMPDBLOG01 - 200GB
    * ULOG01      - 200GB
 
 ### Note: This blueprint use older version of karan to execute script on target machine
