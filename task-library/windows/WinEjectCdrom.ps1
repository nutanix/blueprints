$sh = New-Object -ComObject "Shell.Application"
$sh.Namespace(17).Items() | 
    Where-Object { $_.Type -eq "CD Drive" } | 
        foreach { $_.InvokeVerb("Eject") }