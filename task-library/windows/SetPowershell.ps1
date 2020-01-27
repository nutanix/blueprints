#SetPowershell.ps1

#install the NuGet package provider so that we can install modules from the PowerShell Gallery
try {
    $result = Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -ErrorAction Stop
    Write-Host "INFO: Installed NuGet package provider"
}
catch {throw "ERROR: installing package NuGet : $($_.Exception.Message)"}
write-host "Package $($result.name):$($result.version) was successfully installed" -ForegroundColor Green

#trust the Windows PowerShell Gallery repository
try {
    $result = Set-PSRepository -Name "PSGallery" -InstallationPolicy Trusted -ErrorAction Stop
    Write-Host "INFO: Now trusting the Powershell Gallery"
}
catch {throw "ERROR: trusting the PowerShell Gallery repository : $($_.Exception.Message)"}

$Error.Clear() #required as PoSH populates $error even though the cmdlet completed successfully