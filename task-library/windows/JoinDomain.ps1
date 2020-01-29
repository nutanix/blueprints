# region headers
# posh-api-template v20190604 / stephane.bourdeaud@nutanix.com
#* author:       stephane.bourdeaud@nutanix.com
#* version:      11/14/2019
#  task_name:    JoinDomain
#  description:  Joins the specified Active Directory domain
# endregion

#region capture Calm variables
$ad_username = "@@{ad_credentials.username}@@"
$ad_username_secret = "@@{ad_credentials.secret}@@"
$ad_domain = "@@{ad_domain}@@"
#endregion

#converting password to something we can use
$adminpassword = ConvertTo-SecureString -asPlainText -Force -String "$ad_username_secret"
#creating the credentials object based on the Calm variables
$credential = New-Object System.Management.Automation.PSCredential($ad_username,$adminpassword)

#joing the domain
try {
    $result = add-computer -domainname $ad_domain -Credential ($credential) -Force -Options JoinWithNewName,AccountCreate -PassThru -ErrorAction Stop -Verbose
    Write-Host "INFO: Successfully joined Active Directory domain $ad_domain"
}
catch {Throw "ERROR: Could not join Active Directory domain : $($_.Exception.Message)"}
