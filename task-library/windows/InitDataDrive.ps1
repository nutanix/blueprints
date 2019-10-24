Get-Disk | Where-Object IsOffline –Eq $True | Set-Disk –IsOffline $False
Initialize-Disk -Number 1 -PartitionStyle GPT
New-Partition -DiskNumber 1 -UseMaximumSize -AssignDriveLetter
Format-Volume -DriveLetter ((Get-Partition -DiskNumber 1 -PartitionNumber 2).DriveLetter)