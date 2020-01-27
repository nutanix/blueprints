# Tested on Windows Server 2019

#change UI settings to max performance (for the administrator user)
Write-Host "INFO: Changing UI settings to max performance"
New-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name VisualFXSetting -Value 2

#disable background image
Write-Host "INFO: Disabling background image"
New-ItemProperty -Path "HKLM:\Software\Policies\Microsoft\Windows\System" -Name DisableLogonBackgroundImage -Value 1

#disable paging executive
Write-Host "INFO: Disabling paging executive"
Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Session Manager\Memory Management" -Name DisablePagingExecutive -Value 1

#enable Ultimate Performance Power Plan
if (!(powercfg -l | %{if($_.contains("Ultimate Performance")) {$_.split()[3]}})) {
    Write-Host "INFO: Adding Ultimate Performance power plan"
    powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61
}
#set power plan to Ultimate Performance
$ultimate = powercfg -l | %{if($_.contains("Ultimate Performance")) {$_.split()[3]}} | Select -First 1
try {
    powercfg -setactive $ultimate
    Write-Host "INFO: Set power plan to Ultimate Performance"
}
catch {
    Throw "ERROR: Could not set power plan to Ultimate Performance : $($_.Exception.Message)"
}

#disable scheduled tasks
Write-Host "INFO: Disabling scheduled tasks"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\Autochk\Proxy"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\Bluetooth\UninstallDeviceTask"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\Defrag\ScheduledDefrag"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\Diagnosis\Scheduled"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticResolver"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\Location\Notifications"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\Maintenance\WinSAT"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\Maps\MapsToastTask"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\Maps\MapsUpdateTask"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\MemoryDiagnostic\ProcessMemoryDiagnosticEvents"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\MemoryDiagnostic\RunFullMemoryDiagnostic"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\Mobile Broadband Accounts\MNO Metadata Parser"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\Power Efficiency Diagnostics\AnalyzeSystem"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\Ras\MobilityManager"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\RecoveryEnvironment\VerifyWinRE"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\Registry\RegIdleBackup"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\UPnP\UPnPHostConfig"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\WDI\ResolutionHost"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\Customer Experience Improvement Program\consolidator"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\Customer Experience Improvement Program\usbceip"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\DiskCleanup\SilentCleanup"
Disable-ScheduledTask -TaskName "\Microsoft\Windows\Servicing\StartComponentCleanup"