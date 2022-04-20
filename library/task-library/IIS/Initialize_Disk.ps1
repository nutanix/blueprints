$DataDrive="@@{DATA_DRIVE}@@"

Write-Output "Initalizing All the Data Disks"

if ($(Get-Disk).count -gt 1) {
    Get-Disk | ForEach-Object {
        if ($_.Number -eq 0){
            Write-Output "Ignoring OS disk"
        } elseif ($_.Number -eq 1) {
            $disk_number = $_.Number
            Get-Disk -Number $_.Number | Initialize-Disk -ErrorAction SilentlyContinue
            New-Partition -DiskNumber $_.Number -DriveLetter $DataDrive -UseMaximumSize -ErrorAction SilentlyContinue 
            Format-Volume -DriveLetter $DataDrive -FileSystem NTFS -NewFileSystemLabel "Data" -Confirm:$false
        } else {
            $disk_number = $_.Number
            Get-Disk -Number $disk_number | Initialize-Disk -ErrorAction SilentlyContinue
        }
    }
}