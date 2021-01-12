##############################################
# Name        : JoinDomain.ps1
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to JoinDomain 
# Compatibility : Windows2016
##############################################

$User = "@@{Domain}@@\administrator"
$Server = "@@{AD_SERVER}@@"
$Password = ConvertTo-SecureString "@@{AD_admin_password}@@" –AsPlaintext –Force
$cred = New-Object System.Management.Automation.PsCredential($User,$Password)
$adapter = Get-NetAdapter | ? {$_.Status -eq "up"}
$adapter | Set-DnsClientServerAddress -ServerAddresses $Server
Add-Computer -DomainName "@@{Domain}@@" -Credential $cred

Restart-computer -Force
