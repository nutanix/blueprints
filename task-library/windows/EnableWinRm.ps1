#run winrm quickconfig
winrm quickconfig
#enable WinRm thru the Windows firewall
netsh advfirewall firewall add rule dir=in name="WinRm" action=allow enable=yes profile=any protocol=TCP localport=5985
#enable PsRemoting
Enable-PSRemoting -SkipNetworkProfileCheck -Force
#set ExecutionPolicy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Force
