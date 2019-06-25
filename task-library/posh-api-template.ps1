# region DELETE ME AFTER READING
# ! Meant to be edited in VSCode w/ the BetterComments extension installed
# * Conventions:
# * Aiming for the the following standards:
# * https://github.com/PoshCode/PowerShellPracticeAndStyle
# * Otherwise use PEP8 when in doubt (https://pep8.org/)
# 1. use all lower case for variable names.
# 2. when composing variable names, use underscore to separate words. 
#    Exp: username_secret. Use this same convention in Calm.
# 3. name sections with comments, comment line after the code.
# 4. don't print secrets, including tokens. Favor authentication 
#    (login/logout) in each script.
# 5. when saving your script, name it as the task name appears in Calm,
#    using the following convention: NameOfIntegrationPointAPIendpointMethod.ps1
# 6. use double quotes first, then single quotes.
# 7. Try your best and keep line length under 80 characters, even though
#    it makes your eyes bleed.
# endregion

# region headers
# posh-api-template v20190604 / stephane.bourdeaud@nutanix.com
# TODO Fill in this section with your information
# author:       <your email address here>
# version:      <date / notes>
# task_name:    <enter the name of the task as it appears in your bp>
# description:  
# endregion

#region capture Calm variables
# * Capture variables here. This makes sure Calm macros are not referenced 
# * anywhere else in order to improve maintainability.
$username = '@@{credname.username}@@'
$username_secret = "@@{credname.secret}@@"
$api_server = "@@{endpoint_ip}@@"
#endregion

#region prepare api call
$api_server_port = "443"
$api_server_endpoint = "/apis/batch/v1/"
$url = "https://{0}:{1}{2}" -f $api_server,$api_server_port, `
    $api_server_endpoint
$method = "POST"
$headers = @{
    "Authorization" = "Basic "+[System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($username+":"+$username_secret));
    "Content-Type"="application/json";
    "Accept"="application/json"
}


# this is used to capture the content of the payload
$content = @{
    property1="value";
    property2=@{
        property21="value";
        property22="value"
    };
    property3="value"
}
$payload = (ConvertTo-Json $content -Depth 4)

    
# ignore SSL warnings
Write-Host "$(Get-Date) [INFO] Ignoring invalid certificates"
if (-not ([System.Management.Automation.PSTypeName]'ServerCertificateValidationCallback').Type) {
    $certCallback = @"
    using System;
    using System.Net;
    using System.Net.Security;
    using System.Security.Cryptography.X509Certificates;
    public class ServerCertificateValidationCallback
    {
        public static void Ignore()
        {
            if(ServicePointManager.ServerCertificateValidationCallback ==null)
            {
                ServicePointManager.ServerCertificateValidationCallback += 
                    delegate
                    (
                        Object obj, 
                        X509Certificate certificate, 
                        X509Chain chain, 
                        SslPolicyErrors errors
                    )
                    {
                        return true;
                    };
            }
        }
    }
"@
    Add-Type $certCallback
}
[ServerCertificateValidationCallback]::Ignore()


# add Tls12 support
Write-Host "$(Get-Date) [INFO] Adding Tls12 support"
[Net.ServicePointManager]::SecurityProtocol = `
    ([Net.ServicePointManager]::SecurityProtocol -bor `
    [Net.SecurityProtocolType]::Tls12)
#endregion

#region make api call
try {
    Write-Host "$(Get-Date) [INFO] Making a $method call to $url"
    $resp = Invoke-RestMethod -Method $method -Uri $url -Headers $headers `
        -Body $payload -ErrorAction Stop
    Write-Host "$(Get-Date) [INFO] Response Metadata: $($resp.metadata `
        | ConvertTo-Json)"
    # response data will be an array in $resp.entities
    Write-Host "$(Get-Date) [INFO] Showing entities in response:"
    ForEach ($entity in $resp.entities) {
        $entity | Format-List #expose the data structure of entities
    }
}
catch {
    $saved_error = $_.Exception.Message
    # Write-Host "$(Get-Date) [INFO] Headers: $($headers | ConvertTo-Json)"
    Write-Host "$(Get-Date) [INFO] Payload: $payload"
    Throw "$(get-date) [ERROR] $saved_error"
}
finally {
    #add any last words here; this gets processed no matter what
    Write-Host "$(Get-Date) [INFO] Response variable structure:"
    $resp | Format-List
}
#endregion