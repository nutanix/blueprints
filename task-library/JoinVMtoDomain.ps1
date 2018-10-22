#############################################################
# Name        : JoinVMtoDomain
# Author      : Calm Devops
# Version     : 1.0
# Description : Script is used to join windows vm to domain.
# Compatibility : Windows Serever 2012, 2012 R2, 2016, Win 10
#############################################################

if (("@@{DOMAIN}@@" == "") -and ("@@{DOMAIN_CRED.username}@@" -eq "") -and ("@@{DOMAIN_CRED.secret}@@" -eq "") -and ("@@{AD_IP}@@" -eq "")){
    Write-Output "ERROR: 'DOMAIN', 'AD_IP' and creds are mandatory."
    exit 1
}

# -*- JointoDomain joins the VM to the domain.
function JointoDomain {
  [CmdletBinding()]
  Param(
      [parameter(Mandatory=$true)]
      [string]$DomainName,
      [parameter(Mandatory=$false)]
      [string]$OU,
      [parameter(Mandatory=$true)]
      [string]$Username,
      [parameter(Mandatory=$true)]
      [string]$Password,
      [parameter(Mandatory=$true)]
      [string]$Server
  )
  $adapter = Get-NetAdapter | ? {$_.Status -eq "up"}
  $adapter | Set-DnsClientServerAddress -ServerAddresses $Server

  if ($env:computername  -eq $env:userdomain) {
    Write-Output "Not in domain"
    $adminname = "$Username"
    $adminpassword = ConvertTo-SecureString -asPlainText -Force -String "$Password"
    $credential = New-Object System.Management.Automation.PSCredential($adminname,$adminpassword)
    Add-computer -DomainName $DomainName -Credential $credential -force -Options JoinWithNewName,AccountCreate -PassThru -ErrorAction Stop
  } else {
    Write-Output "WARNING: Already in domain"
  }
}

JointoDomain -DomainName "@@{DOMAIN}@@" -Username "@@{DOMAIN_CRED.username}@@" -Password "@@{DOMAIN_CRED.secret}@@" -Server "@@{AD_IP}@@"

Restart-Computer -Force -AsJob
exit 0
