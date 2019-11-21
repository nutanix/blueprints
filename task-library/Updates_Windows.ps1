Install-PackageProvider -Name NuGet -Force
Install-Module PSWindowsUpdate -Force
Install-WindowsUpdate -ScheduleJob (Get-Date).AddMinutes(1) -confirm:$false -IgnoreReboot
start-sleep -seconds 90
$taskStatus = (get-scheduledtask).where{$_.TaskName -eq "PSWindowsUpdate"}
while ($taskStatus.State -eq "Running"){
    $taskStatus = (get-scheduledtask).where{$_.TaskName -eq "PSWindowsUpdate"}
    start-sleep -seconds 300
    }
Write-host "Task execution completed"
$taskStatus.State
(Get-ScheduledTask).where{$_.TaskName -eq "PSWindowsUpdate"} | Unregister-ScheduledTask -Confirm:$false
Restart-Computer -Force
exit 0
