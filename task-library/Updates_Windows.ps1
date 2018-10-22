######################################################
# Name        : JoinVMtoDomain
# Author      : Calm Devops
# Version     : 1.0
# Description : Pre-packaged task for Windows updates.
# Compatibility : Windows Serever 2012, 2012 R2, 2016
######################################################

Install-PackageProvider -Name NuGet -Force
Install-Module PSWindowsUpdate -Force
Add-WUServiceManager -ServiceID 7971f918-a847-4430-9279-4a52d1efe18d -Silent -Confirm:$false
Get-WUInstall –MicrosoftUpdate –AcceptAll
