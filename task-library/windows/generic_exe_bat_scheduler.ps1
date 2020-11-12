$Scheduler_Name = "Test-Scheduer-@@{calm_unique}@@-calm"
$cmd_with_args = "@@{CMD_WITH_ARGS}@@"  #eg. "C:\temp\abcd.exe -install /verysilent"
$cmd_trigrd_process = "@@{CMD_TRIGRD_PROCESS}@@"
Schtasks /create /TN $Scheduler_Name /SC ONCE /TR $cmd_with_args  /ST "00:00" /SD "01/01/1901" /F
echo "Scheduler Details"
SCHTASKS /TN $Scheduler_Name
echo "Triggering Scheduler"
schtasks /Run /TN $Scheduler_Name
echo "get-process"
get-process "*$cmd_trigrd_process*"
echo "deleting scheduler"
SCHTASKS /Delete /TN $Scheduler_Name /F
