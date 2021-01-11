New-NetFirewallRule -DisplayName 'IIS HTTP port 80' -Profile Any -Direction Inbound -Action Allow -Protocol TCP -LocalPort 80
New-NetFirewallRule -DisplayName 'IIS HTTPS port 443' -Profile Any -Direction Inbound -Action Allow -Protocol TCP -LocalPort 443
