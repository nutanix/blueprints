$DOMAIN = "@@{DOMAIN}@@"
$DOMAIN_USERNAME = "@@{DOMAIN_CRED.username}@@"
$DOMAIN_PASSWORD = "@@{DOMAIN_CRED.secret}@@"
$AD_IP = "@@{AD_IP}@@"

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
    Write-Host "Not in domain"
    $adminname = "$Username"
    $adminpassword = ConvertTo-SecureString -asPlainText -Force -String "$Password"
    Write-Host "$adminname , $password"
    $credential = New-Object System.Management.Automation.PSCredential($adminname,$adminpassword)
    Add-computer -DomainName $DomainName -Credential $credential -force -Options JoinWithNewName,AccountCreate -PassThru -ErrorAction Stop
  } else {
     Write-Host "Already in domain"
  }
}

JointoDomain -DomainName $DOMAIN -Username $DOMAIN_USERNAME -Password $DOMAIN_PASSWORD -Server $AD_IP

Start-Process -FilePath "shutdown.exe" -ArgumentList ("/r", "/t", "5")
exit 0
