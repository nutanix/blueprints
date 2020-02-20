#schedule an installation of all applicable patches 2 minutes from now and automatically reboot. Do this for 3 reboot cycles (after each cycle, updates will be checked again and installed if required)
try {Get-WUInstall -AcceptAll -Verbose -Install -AutoReboot -RecurseCycle 3 -ScheduleJob ((Get-Date).Addminutes(2)) -PSWUSettings @{SmtpServer="@@{smtp_server}@@";From="@@{wu_rpt_from}@@";To="@@{wu_rpt_recipient}@@";Port=@@{smtp_port}@@} -ErrorAction Stop}
catch {throw "Error scheduling Windows Update patch installation : $($_.Exception.Message)"}
write-host "Successfully scheduled Windows Update patch installation." -ForegroundColor Green

#display the scheduled job
try {Get-WUJob -ErrorAction Stop}
catch {throw "Error displaying Windows Update job : $($_.Exception.Message)"}

#display details fo the scheduled task
try {Get-ScheduledTask -TaskName PSWindowsUpdate -ErrorAction Stop | Select -Property TaskName,Date,State}
catch {throw "Error displaying Windows Update scheduled task details: $($_.Exception.Message)"}

#display scheduled task detailed action
try{(Get-ScheduledTask -TaskName PSWindowsUpdate -ErrorAction Stop).Actions}
catch {throw "Error displaying Windows Update scheduled task action details : $($_.Exception.Message)"}