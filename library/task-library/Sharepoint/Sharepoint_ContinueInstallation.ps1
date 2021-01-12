##############################################
# Name        : SHarepoint_ContinueInstallation.ps1 
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to continue installation post prerequisites installation.
# Compatibility : Windows2016
##############################################

cd $HOME
$Outfile=$PWD.Path + "\officeserver.img"

Mount-DiskImage -ImagePath  $Outfile 
$driveLetter = (Get-DiskImage -ImagePath $Outfile | Get-Volume).DriveLetter 

$driveLetter += ':'

$SetupPath = $driveLetter + '\setup.exe'
$PreReqPath = $driveLetter +'\prerequisiteinstaller.exe'
$PreReqFiles = "C:\SharePoint_Prerequisites\PrerequisiteInstaller"

echo '
<!-- http://technet.microsoft.com/en-us/library/cc287749.aspx -->

<Configuration>  
  <!-- Package ID for SharePoint Foundation -->
  <Package Id="sts">
    <Setting Id="LAUNCHEDFROMSETUPSTS" Value="Yes"/>
  </Package>

  <!-- Package ID for SharePoint Server -->
  <Package Id="spswfe">
    <Setting Id="SETUPCALLED" Value="1"/>
    <!-- 0 Std | 1 Ent -->
    <Setting Id="OFFICESERVERPREMIUM" Value="1" />
  </Package>

  <PIDKEY Value="@@{LicenceKey}@@"/>
  <Setting Id="SERVERROLE" Value="APPLICATION"/>
  <Setting Id="USINGUIINSTALLMODE" Value="0"/>
  <Setting Id="SETUPTYPE" Value="CLEAN_INSTALL"/>
  <Setting Id="SETUP_REBOOT" Value="Never"/>
  <Setting Id="AllowWindowsClientInstall" Value="True"/>
  <ARP ARPCOMMENTS="" ARPCONTACT="" />
  <Display Level="basic" CompletionNotice="No" AcceptEula="Yes"/>
  <Logging Type="verbose" Path="%temp%" Template="SharePoint Server Setup(*).log"/>
</Configuration>   ' > Installation.xml


$Username = "Administrator"  
$Password = ConvertTo-SecureString 'xxxxxxx' -AsPlainText -Force
$adminCredential = New-Object System.Management.Automation.PSCredential $Username, $Password
$Session = New-PSSession  -Credential $adminCredential

$silentArgs = "/config $pwd\Installation.xml"
echo "$SetupPath $silentArgs"
$sb = [scriptblock]::create("$SetupPath $silentArgs")

$s = New-PSSession -computerName "localhost" -Credential $adminCredential
Invoke-Command -Session $s -ScriptBlock $sb

$ps = Get-Process *setup*
while ($ps -ne $null){
$ps = Get-Process *setup*
sleep(10)
}

Remove-PSSession $s

exit(0)
