$WS2008R2_MAJOR                 = '6.1'
$WS2012_MAJOR                   = '6.2'
$WS2012R2_MAJOR                 = '6.3'
$WS2016_MAJOR                   = '10.0'

# -*- Checks AD Domain services Installation
function Check-ActiveDirectoryFeature {
   return $(Get-WindowsFeature AD-Domain-Services -ErrorAction SilentlyContinue).Installed
}
# -*- Installs AD Domain services
function Install-ActiveDirectory {
  Write-Output "Installing AD Features."
  Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
}
# -*- Checks the pre existance of domain
function Check-DomainExistance {
  #if (Get-ADDomainController -Discover -ErrorAction SilentlyContinue){
  if ("$((wmic ComputerSystem get DomainRole)[2])".trim() -eq "5"){
   return $true
  }
  else{
    return $false
  }
}
# -*- Gets Machine IP address, Netmask, DNS and prefix
function Get-ServerIPAddress {
  $IPType = "IPv4"
  $IPv4Address = $(Get-NetAdapter | ? {$_.Status -eq "up"}| Get-NetIPAddress | ? {$_.AddressFamily -eq "IPv4"}).IPv4Address
  $Prefix = $(Get-NetAdapter | ? {$_.Status -eq "up"} | Get-NetIPAddress).PrefixLength[1]
  $Gateway = "$((Get-WmiObject Win32_NetworkAdapterConfiguration -EA Stop | ? {$_.IPEnabled}).DefaultIPGateway)"
  $DNS = $(Get-NetAdapter | ? {$_.Status -eq "up"} | Get-DnsClientServerAddress | ? {$_.AddressFamily -eq 2}).ServerAddresses
  return $IPType, $IPv4Address, $Prefix, $Gateway, $DNS
}
# -*- Removes DHCP IP sets the Static ips which it has got from Get-ServerIPAddress.
function Set-StaticIpAddress {
  [CmdletBinding()]
  Param(
      [parameter(Mandatory=$true)]
      [string]$Name,
      [parameter(Mandatory=$true)]
      [string]$IPType,
      [parameter(Mandatory=$true)]
      [string]$IPv4Address,
      [parameter(Mandatory=$true)]
      [string]$Prefix,
      [parameter(Mandatory=$false)]
      [string]$Gateway,
      [parameter(Mandatory=$false)]
      [array]$DNS
  )

  $adapter = Get-NetAdapter -Name $Name | ? {$_.Status -eq "up"}
  If (($adapter | Get-NetIPConfiguration).IPv4Address.IPAddress) {
      $adapter | Remove-NetIPAddress -AddressFamily $IPType -Confirm:$false
  }
  If (($adapter | Get-NetIPConfiguration).Ipv4DefaultGateway) {
      $adapter | Remove-NetRoute -AddressFamily $IPType -Confirm:$false
  }
  if ($Gateway){
    $adapter | New-NetIPAddress -AddressFamily $IPType -IPAddress "$IPv4Address" -PrefixLength $Prefix -DefaultGateway "$Gateway"
  }
  else{
    $adapter | New-NetIPAddress -AddressFamily $IPType -IPAddress "$IPv4Address" -PrefixLength $Prefix
  }
  if ($DNS){
    $adapter | Set-DnsClientServerAddress -ServerAddresses $DNS
  }
}

# -*- Configures AD Domain service
function Configure-ActiveDirectory {
  [CmdletBinding()]
  Param(
      [parameter(Mandatory=$true)]
      [string]$DomainName,
      [parameter(Mandatory=$true)]
      [string]$Password,
      [parameter(Mandatory=$false)]
      [string]$DatabasePath="C:\Windows\NTDS",
      [parameter(Mandatory=$true)]
      [string]$DomainMode,
      [parameter(Mandatory=$true)]
      [string]$ForestMode,
      [parameter(Mandatory=$false)]
      [string]$LogPath="C:\Windows\NTDS",
      [parameter(Mandatory=$false)]
      [string]$SysvolPath="C:\Windows\SYSVOL",
      [parameter(Mandatory=$true)]
      [string]$DomainType,
      [parameter(Mandatory=$false)]
      [string]$ChildDomainName
  )
  Import-Module ADDSDeployment

  $secpasswd = ConvertTo-SecureString $Password -AsPlainText -Force
  $credential = New-Object System.Management.Automation.PSCredential("$DomainName\administrator",$secpasswd)
  $netbios = $DomainName.Split(".")[0].ToUpper()
  Write-Output "Configuring Domain services."
  switch ($DomainType){
    "DC"{
      Install-ADDSForest -CreateDnsDelegation:$false -DatabasePath $DatabasePath -DomainMode $DomainMode -DomainName $DomainName -DomainNetbiosName $netbios -ForestMode $ForestMode -InstallDns:$true -LogPath $LogPath -NoRebootOnCompletion:$true -SysvolPath $SysvolPath -Force:$true -SafeModeAdministratorPassword $secpasswd
    }
    "ADC"{
      Install-ADDSDomainController -NoGlobalCatalog:$false -CreateDnsDelegation:$false -CriticalReplicationOnly:$false -DatabasePath $DatabasePath -DomainName $DomainName -InstallDns:$true -LogPath $LogPath -NoRebootOnCompletion:$true -SiteName "Default-First-Site-Name" -SysvolPath $SysvolPath -Force:$true -SafeModeAdministratorPassword $secpasswd -Credential $credential
    }
    "CDC"{
      Install-ADDSDomain -NoGlobalCatalog:$false -CreateDnsDelegation:$true -DatabasePath $DatabasePath -DomainMode $DomainMode -DomainType "ChildDomain" -InstallDns:$true -LogPath $LogPath -NewDomainName $ChildDomainName -NewDomainNetbiosName $ChildDomainName.ToUpper() -ParentDomainName $DomainName -NoRebootOnCompletion:$true -SiteName "Default-First-Site-Name" -SysvolPath $SysvolPath -Force:$true -SafeModeAdministratorPassword $secpasswd -Credential $credential
    }
    "RODC"{
      Install-ADDSDomainController -AllowPasswordReplicationAccountName @("$netbios\Allowed RODC Password Replication Group") -NoGlobalCatalog:$false -CriticalReplicationOnly:$false -DatabasePath $DatabasePath -DenyPasswordReplicationAccountName @("BUILTIN\Administrators", "BUILTIN\Server Operators", "BUILTIN\Backup Operators", "BUILTIN\Account Operators", "$netbios\Denied RODC Password Replication Group") -DomainName $DomainName -InstallDns:$true -LogPath $LogPath -NoRebootOnCompletion:$true -ReadOnlyReplica:$true -SiteName "Default-First-Site-Name" -SysvolPath $SysvolPath -Force:$true -SafeModeAdministratorPassword $secpasswd -Credential $credential
    }
    default{
      Write-Output "Invalid DomainType"
    }
}
}
# -*- Checks whether server has DHCP IP or Static IP.
# -*- If DHCP it gets IP Details and sets them statically.
if ($(Get-WmiObject -Class Win32_NetworkAdapterConfiguration -Filter IPEnabled=TRUE).DHCPEnabled){
  $IPType, $IPv4Address, $Prefix, $Gateway, $DNS = Get-ServerIPAddress
  if ("DC" -eq "DC"){
    $DNS = "127.0.0.1"
  }
  if (($IPType -eq $Null) -or ($IPv4Address -eq $Null) -or ($Prefix -eq $Null) -or ($Gateway -eq $Null)){
    Write-Output "Please pass ipaddress, prefix and gateway address."
  }
  else{
    Set-StaticIpAddress "Ethernet" $IPType $IPv4Address $Prefix $Gateway $DNS
  }
}
else{
  Write-Output "Static IP Is already set"
}

if (Check-ActiveDirectoryFeature){
  Write-Output "Active Directory already installed."
}
else{
  Install-ActiveDirectory
}

if (Check-DomainExistance){
  Write-Output "Domain exists already."
}
else{
  $MajorOSVersion= [string](Get-WmiObject Win32_OperatingSystem | Select-Object @{n="Major";e={($_.Version.Split(".")[0]+"."+$_.Version.Split(".")[1])}}).Major
  if ($MajorOSVersion -eq $WS2012R2_MAJOR){
    $DomainMode = "Win2012R2"
  }elseif ($MajorOSVersion -eq $WS2016_MAJOR){
    $DomainMode = "WinThreshold"
  }
  Configure-ActiveDirectory -DomainName "@@{DOMAIN}@@" -Password "@@{DOMAIN_CRED.secret}@@" -DomainMode $DomainMode -ForestMode $DomainMode -DomainType "@@{DOMAIN_TYPE}@@" -ChildDomainName "@@{CHILD_DOMAIN}@@"
}

Start-Sleep -Seconds 5
Start-Process -FilePath "shutdown.exe" -ArgumentList ("/r", "/t", "5")
exit 0
