##############################################
# Name        : Sharepoint_InstallPrereq.ps1
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to download and start sharepoint prerequisites.
# Compatibility : Windows2016
##############################################

cd $HOME
$imageUrl="https://download.microsoft.com/download/0/0/4/004EE264-7043-45BF-99E3-3F74ECAE13E5/officeserver.img"
$Outfile=$PWD.Path + "\officeserver.img"
$wc = New-Object System.Net.WebClient
$wc.DownloadFile($imageUrl, $Outfile)

Mount-DiskImage -ImagePath  $Outfile 
$driveLetter = (Get-DiskImage -ImagePath $Outfile | Get-Volume).DriveLetter 

$driveLetter += ':'

$SetupPath = $driveLetter + '\setup.exe'
$PreReqPath = $driveLetter +'\prerequisiteinstaller.exe'

Import-Module Servermanager

$PreReqFiles = "C:\SharePoint_Prerequisites\PrerequisiteInstaller"
mkdir $PreReqFiles

$DownloadURL = "https://download.microsoft.com/download/F/3/C/F3C64941-22A0-47E9-BC9B-1A19B4CA3E88/ENU/x64/sqlncli.msi"
$wc.DownloadFile($DownloadURL,"$PreReqFiles\sqlncli-2012.msi")

$DownloadURL = "https://download.microsoft.com/download/5/7/2/57249A3A-19D6-4901-ACCE-80924ABEB267/ENU/x86/msodbcsql.msi"
$wc.DownloadFile($DownloadURL,"$PreReqFiles\msodbcsql.msi")

echo "Prerequisites installation"
$silentArgs = "/SQLNCli:$PreReqFiles\sqlncli-2012.msi /unattended"
$install = Start-Process -FilePath $PreReqPath -ArgumentList $silentArgs -Wait -NoNewWindow -PassThru
$install.WaitForExit()

$exitCode = $install.ExitCode
$install.Dispose()
sleep(100)

$ps = Get-Process | where {$_.name -eq "prerequisiteinstaller" }
while ($ps -ne $null){
$ps = Get-Process | where {$_.name -eq "prerequisiteinstaller" }
sleep(10)
}

echo "Enabling credssp"
Enable-WSManCredSSP -Role "server" -Force

echo "Restarting"
Restart-computer -Force

