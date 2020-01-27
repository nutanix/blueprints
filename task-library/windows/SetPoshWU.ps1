#SetPoshWU.ps1

#install the Windows Update PowerShell module
try {
    $result = Install-Module PSWindowsUpdate -Confirm:$false -Force -ErrorAction Stop
    Write-Host "INFO: Installed the PSWindowsUpdate module"
}
catch {throw "ERROR: installing the PSWindowsUpdate module from the PowerShell Gallery: $($_.Exception.Message)"}

#enabling Windows Update remoting
try {
    $result = Enable-WURemoting -Verbose -ErrorAction Stop
    Write-Host "INFO: Enabled Windows Update remoting"
}
catch {throw "ERROR: enabling Windows Update remoting: $($_.Exception.Message)"}

$Error.Clear() #required as PoSH populates $error even though the cmdlet completed successfully