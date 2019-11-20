$VerbosePreference = 'Continue'
$UpdatePath = "C:\Updates"
$LogPathName = Join-Path -Path $UpdatePath -ChildPath "update-log-$(Get-Date -Format 'yyyy.MM.dd-HH.mm').log"
Start-Transcript $LogPathName
$UpdateLocation = "$($UpdatePath)\kb4482887.msu"
$hostfixURL = "http://download.windowsupdate.com/c/msdownload/update/software/updt/2019/02/windows10.0-kb4482887-x64_826158e9ebfcabe08b425bf2cb160cd5bc1401da.msu"

if (!(Test-Path $UpdatePath)){
  New-Item -ItemType Directory -Force -Path $UpdatePath
}

(New-Object System.Net.WebClient).DownloadFile($hostfixURL, $UpdateLocation)

$FileTime = Get-Date -format 'yyyy.MM.dd-HH.mm'

if (!(Test-Path $env:systemroot\SysWOW64\wusa.exe)){
  $Wus = "$env:systemroot\System32\wusa.exe"
} else {
  $Wus = "$env:systemroot\SysWOW64\wusa.exe"
}

$secpasswd = ConvertTo-SecureString "nutanix/4u" -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential("administrator",$secpasswd)

Write-Information "Starting Update $Qty - `r`n$UpdateLocation"
Start-Process -FilePath $Wus -ArgumentList ($UpdateLocation, '/quiet', '/norestart', "/log:$UpdatePath\Wusa.log") -Wait -Credential $credential
Write-Information "Finished Update $Qty"
if (Test-Path $UpdatePath\Wusa.log){
  Rename-Item $UpdatePath\Wusa.log $UpdatePath\Wusa.$FileTime.evtx
}

Stop-Transcript
Start-Process -FilePath "shutdown.exe" -ArgumentList ("/r", "/t", "5")
