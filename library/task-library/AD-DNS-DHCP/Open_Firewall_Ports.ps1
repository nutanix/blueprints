New-NetFirewallRule -DisplayName "AD" -Direction Inbound -Protocol UDP -LocalPort 389 -Action allow
New-NetFirewallRule -DisplayName "DNS TCP" -Direction Inbound -Protocol TCP -LocalPort 53 -Action allow
New-NetFirewallRule -DisplayName "DNS UDP" -Direction Inbound -Protocol UDP -LocalPort 53 -Action allow
New-NetFirewallRule -DisplayName "GC TCP" -Direction Inbound -Protocol TCP -LocalPort 3268 -Action allow
New-NetFirewallRule -DisplayName "GC UDP" -Direction Inbound -Protocol UDP -LocalPort 3269 -Action allow
New-NetFirewallRule -DisplayName "SYSVOL TCP" -Direction Inbound -Protocol TCP -LocalPort 139 -Action allow
New-NetFirewallRule -DisplayName "SYSVOL UDP" -Direction Inbound -Protocol UDP -LocalPort 138 -Action allow
New-NetFirewallRule -DisplayName "KERBROS UDP" -Direction Inbound -Protocol UDP -LocalPort 88 -Action allow
New-NetFirewallRule -DisplayName "AD COM TCP" -Direction Inbound -Protocol TCP -LocalPort 135 -Action allow
New-NetFirewallRule -DisplayName "AD COM UDP" -Direction Inbound -Protocol UDP -LocalPort 135 -Action allow
New-NetFirewallRule -DisplayName "KERBROS PW CHANGE TCP" -Direction Inbound -Protocol TCP -LocalPort 464 -Action allow
New-NetFirewallRule -DisplayName "KERBROS PW CHANGE UDP" -Direction Inbound -Protocol UDP -LocalPort 464 -Action allow
