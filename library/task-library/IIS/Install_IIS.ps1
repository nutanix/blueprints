Write-Output "Installing IIS including Management tools"

Install-WindowsFeature -name Web-Server -IncludeManagementTools
