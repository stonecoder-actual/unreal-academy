# No Pester dependency; test functions without installing a task or touching live data.
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\scripts\Academy.ps1') -LibraryOnly
$script:LogFile = $null
$script:InstallRoot = Join-Path $env:TEMP ('academy-script-check-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force (Join-Path $script:InstallRoot 'Releases') | Out-Null
function Assert($Condition, $Message) { if (-not $Condition) { throw $Message } }

$pretty = "{`n  `"status`": `"ok`",`n  `"nested`": {`"a`": 1}`n}"
Assert ((Get-JsonResult $pretty).nested.a -eq 1) 'Multiline Compose JSON failed'
Assert ((Get-JsonResult "Container started`n{`"ready`":true}").ready) 'Maintenance JSON failed'
$config = @{Project='academy-test';Port=3005;Data=(Join-Path $script:InstallRoot 'Data')}
$override = New-Override $config ('a' * 40)
$yaml = Get-Content -LiteralPath $override -Raw
Assert ($yaml.Contains('127.0.0.1:3005:80')) 'Loopback binding missing'
Assert ($yaml.Contains('ports: !reset []')) 'Backend port reset missing'
$composeArgs = Get-ComposeArguments $config 'C:\Path with spaces\Release' $override
Assert ($composeArgs -contains 'C:\Path with spaces\Release') 'Native argument path was split'

function Invoke-Compose {
    return ($script:Resolved | ConvertTo-Json -Depth 10)
}
$script:Resolved = @{services=@{backend=@{volumes=@(@{target='/data';source=$config.Data},@{target='/courses';source='C:\Courses';read_only=$true})};frontend=@{ports=@(@{host_ip='127.0.0.1';published=3005})}}}
Test-ComposeSafety $config 'unused' 'unused'
$script:Resolved.services.frontend.ports[0].host_ip = '0.0.0.0'
$rejected = $false
try { Test-ComposeSafety $config 'unused' 'unused' } catch { $rejected = $_.Exception.Message -like '*127.0.0.1*' }
Assert $rejected 'Unsafe port publication was accepted'
$script:Resolved.services.frontend.ports[0].host_ip = '127.0.0.1'
$script:Resolved.services.backend.volumes[0].source = 'C:\DifferentData'
$rejected = $false
try { Test-ComposeSafety $config 'unused' 'unused' } catch { $rejected = $_.Exception.Message -like '*database mount*' }
Assert $rejected 'Changed persistent mount was accepted'

# Build and inspect the real definition; never call registration during tests.
$definition = New-UpdateTaskDefinition $config
Assert ($definition.Triggers.Count -eq 2) 'Expected logon and hourly triggers'
Assert ($definition.Actions[0].Arguments.Contains('-Automatic')) 'Scheduled updater does not use automatic mode'
Assert ($definition.Principal.RunLevel -eq 0) 'Scheduled task requests elevated privileges'
Assert ($definition.Settings.MultipleInstances -eq 2) 'Scheduled tasks may overlap'
Write-Host 'PASS: deployment script parsing, JSON, native arguments, loopback/data guards and real task definitions (no registration).'
