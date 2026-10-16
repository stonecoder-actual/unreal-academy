#requires -Version 5.1
[CmdletBinding()]
param(
    [ValidateSet('Install','Update','Check','Status','Backup','ImportGuide','EnableUpdates','DisableUpdates')]
    [string]$Action = 'Install',
    [string]$Root = 'C:\UnrealAcademy',
    [string]$Repository = 'https://github.com/stonecoder-actual/unreal-academy.git',
    [string]$Branch = 'main',
    [string]$CoursesDirectory,
    [string]$SeedDatabase,
    [string]$GuideFile,
    [ValidateRange(1024,65535)][int]$Port = 3000,
    [ValidateRange(10,300)][int]$WaitSeconds = 120,
    [ValidatePattern('^[a-z][a-z0-9-]*$')][string]$Project = 'unreal-academy',
    [switch]$SkipAutoUpdates,
    [switch]$Automatic,
    [switch]$LibraryOnly
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Log([string]$Message) {
    $line = '{0:u} {1}' -f (Get-Date), $Message
    Write-Host $line
    if ($script:LogFile) { Add-Content -LiteralPath $script:LogFile -Value $line }
}

function Invoke-Tool([string]$Executable, [string[]]$Arguments, [switch]$AllowFailure) {
    $previous = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = @(& $Executable @Arguments 2>&1 | ForEach-Object { "$_" })
        $code = $LASTEXITCODE
    } finally { $ErrorActionPreference = $previous }
    if ($code -ne 0 -and -not $AllowFailure) {
        throw "$([IO.Path]::GetFileName($Executable)) failed ($code): $($output -join [Environment]::NewLine)"
    }
    if ($AllowFailure) { return @{ Code=$code; Output=($output -join "`n") } }
    return ($output -join "`n")
}

function Find-Tool([string]$Name, [string[]]$Candidates, [string]$HelpUrl) {
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    foreach ($candidate in $Candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
    }
    throw "$Name is unavailable. Install it from $HelpUrl then reopen PowerShell. No software was installed automatically."
}

function Test-Requirements {
    if ($env:OS -ne 'Windows_NT') { throw 'Use this installer on Windows.' }
    if (-not [Environment]::Is64BitOperatingSystem) { throw '64-bit Windows is required.' }
    # Windows reports usable RAM after hardware reservation: an 8 GB laptop may report ~7.7 GB.
    if ((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory -lt 7GB) { throw 'Docker Desktop requires an 8 GB-class machine or better; see its Windows system requirements.' }
    $script:Git = Find-Tool 'git.exe' @("$env:ProgramFiles\Git\cmd\git.exe", "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe") 'https://git-scm.com/install/windows'
    $script:Docker = Find-Tool 'docker.exe' @("$env:ProgramFiles\Docker\Docker\resources\bin\docker.exe", "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin\docker.exe") 'https://docs.docker.com/desktop/setup/install/windows-install/'
    Invoke-Tool $script:Git @('--version') | Out-Null
    $version = (Invoke-Tool $script:Docker @('compose','version','--short')).Trim().TrimStart('v')
    if ([version]($version -replace '-.*$','') -lt [version]'2.24.4') { throw 'Docker Compose 2.24.4+ is required. Update Docker Desktop.' }
    if ((Invoke-Tool $script:Docker @('info','--format','{{.OSType}}')).Trim() -ne 'linux') {
        throw 'Start Docker Desktop using Linux containers. Setup: https://docs.docker.com/desktop/features/wsl/'
    }
    # Running a Linux engine verifies the chosen WSL/Hyper-V backend operationally.
    $drive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($script:InstallRoot))
    if ($drive.AvailableFreeSpace -lt 10GB) { throw 'At least 10 GB free space is required for builds, plus your course files and backups.' }
    Write-Log "Requirements passed: Git, Docker Linux engine, Compose $version, disk space. Host Python and Node are not needed."
}

function Save-Json([string]$Path, $Value) {
    $temporary = "$Path.new"
    [IO.File]::WriteAllText($temporary, ($Value | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Read-Json([string]$Path) { return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json) }

function Get-ComposeArguments($Config, [string]$Release, [string]$Override) {
    return @('compose','--project-name',$Config.Project,'--project-directory',$Release,
        '--env-file',(Join-Path $script:InstallRoot 'academy.env'),'-f',(Join-Path $Release 'compose.yaml'),'-f',$Override)
}

function Invoke-Compose($Config, [string]$Release, [string]$Override, [string[]]$Command) {
    return Invoke-Tool $script:Docker ((Get-ComposeArguments $Config $Release $Override) + $Command)
}

function New-Override($Config, [string]$Commit) {
    $path = Join-Path $script:InstallRoot "Releases\images-$Commit.yaml"
    $yaml = @"
services:
  backend:
    image: $($Config.Project)-backend:$Commit
    ports: !reset []
  frontend:
    image: $($Config.Project)-frontend:$Commit
    ports: !override
      - "127.0.0.1:$($Config.Port):80"
"@
    [IO.File]::WriteAllText($path, $yaml, [Text.UTF8Encoding]::new($false))
    return $path
}

function Get-JsonResult([string]$Output) {
    if ($Output.Trim().StartsWith('{')) { return ($Output | ConvertFrom-Json) }
    $json = @($Output -split "`n" | Where-Object { $_.Trim().StartsWith('{') })
    if (-not $json.Count) { throw "Expected maintenance result, got: $Output" }
    return ($json[-1] | ConvertFrom-Json)
}

function Invoke-Maintenance($Config, $Release, $Override, [string[]]$Command) {
    return Get-JsonResult (Invoke-Compose $Config $Release $Override (@('run','--rm','--no-deps','-T','backend','python','-m','app.maintenance') + $Command))
}

function Test-ComposeSafety($Config, $Release, $Override) {
    $resolved = Get-JsonResult (Invoke-Compose $Config $Release $Override @('config','--format','json'))
    foreach ($property in $resolved.services.PSObject.Properties) {
        $service = $property.Value
        if ($service.PSObject.Properties.Name -contains 'ports') {
            foreach ($binding in $service.ports) {
                if ($binding.host_ip -ne '127.0.0.1') { throw 'Deployment refused: a port is not bound to 127.0.0.1.' }
            }
        }
    }
    $mount = @($resolved.services.backend.volumes | Where-Object { $_.target -eq '/data' })
    $courses = @($resolved.services.backend.volumes | Where-Object { $_.target -eq '/courses' })
    if ($mount.Count -ne 1 -or [IO.Path]::GetFullPath($mount[0].source) -ne [IO.Path]::GetFullPath($Config.Data)) {
        throw 'Deployment refused: the persistent database mount changed.'
    }
    if ($courses.Count -ne 1 -or -not $courses[0].read_only) { throw 'Course library must be mounted read-only.' }
}

function New-UpdateTaskDefinition($Config) {
    $scriptFile = Join-Path $script:InstallRoot 'Tools\Academy.ps1'
    $arguments = '-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "{0}" -Action Update -Root "{1}" -Automatic' -f $scriptFile,$script:InstallRoot
    $action = New-ScheduledTaskAction -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -Argument $arguments
    $account = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    $logon = New-ScheduledTaskTrigger -AtLogOn -User $account
    $logon.Delay = 'PT2M'
    $hourly = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(5) -RepetitionInterval (New-TimeSpan -Hours 1)
    $principal = New-ScheduledTaskPrincipal -UserId $account -LogonType Interactive -RunLevel Limited
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 45)
    return (New-ScheduledTask -Action $action -Trigger @($logon,$hourly) -Principal $principal -Settings $settings -Description 'Check the configured Unreal Academy Git branch and deploy while learner records are idle.')
}

function Register-Updates {
    $config = Read-Json $script:ConfigPath
    $definition = New-UpdateTaskDefinition $config
    Register-ScheduledTask -TaskName "$($config.Project)-updates" -InputObject $definition -Force | Out-Null
    Write-Log 'Automatic updates enabled for this Windows account: logon and hourly, while logged in and on AC power.'
}

function Archive-Pending {
    if (Test-Path -LiteralPath $script:PendingPath) {
        Move-Item -LiteralPath $script:PendingPath -Destination (Join-Path $script:InstallRoot ("Logs\transaction-{0}.json" -f [guid]::NewGuid().ToString('N')))
    }
}

function Complete-Release($Commit,$Release,$Override) {
    Save-Json $script:StatePath @{Commit=$Commit;Release=$Release;Override=$Override;UpdatedAt=(Get-Date).ToUniversalTime().ToString('o')}
    New-Item -ItemType Directory -Force (Join-Path $script:InstallRoot 'Tools') | Out-Null
    Copy-Item -LiteralPath (Join-Path $Release 'scripts\Academy.ps1') -Destination (Join-Path $script:InstallRoot 'Tools\Academy.ps1') -Force
    Archive-Pending
}

function Recover-InterruptedDeployment($Config) {
    if (-not (Test-Path -LiteralPath $script:PendingPath)) { return }
    $pending = Read-Json $script:PendingPath
    Write-Log 'Recovering an interrupted deployment from retained local images before contacting Git.'
    if ($pending.Exposed) {
        # Never overwrite potential new learner writes after the frontend was exposed.
        Invoke-Compose $Config $pending.Release $pending.Override @('up','-d','--no-build','--wait','--wait-timeout',"$WaitSeconds") | Out-Null
        $health = Invoke-RestMethod "http://127.0.0.1:$($Config.Port)/api/health" -TimeoutSec 15
        if ($health.status -ne 'ok' -or $health.database -ne 'ok') { throw 'Interrupted release is still unhealthy; latest data retained.' }
        Complete-Release $pending.Commit $pending.Release $pending.Override
    } else {
        Invoke-Compose $Config $pending.Release $pending.Override @('stop','frontend','backend') | Out-Null
        if ($pending.Snapshot -and -not $pending.Snapshot.empty) {
            Invoke-Maintenance $Config $pending.Release $pending.Override @('restore','--snapshot',$pending.Snapshot.backup) | Out-Null
        }
        if ($pending.Previous) {
            Invoke-Compose $Config $pending.Previous.Release $pending.Previous.Override @('up','-d','--no-build','--wait','--wait-timeout',"$WaitSeconds") | Out-Null
        }
        Archive-Pending
    }
    Write-Log 'Interrupted deployment recovered without discarding learner writes.'
}

function Deploy-Version($Config, [switch]$FirstInstall) {
    Recover-InterruptedDeployment $Config
    $source = Join-Path $script:InstallRoot 'Source'
    if ((Invoke-Tool $script:Git @('-C',$source,'status','--porcelain')).Trim()) { throw 'Source checkout has local changes. Preserve them and use a clean deployment checkout; no reset/stash was performed.' }
    Invoke-Tool $script:Git @('check-ref-format','--branch',$Config.Branch) | Out-Null
    $env:GIT_TERMINAL_PROMPT = '0'
    $env:GCM_INTERACTIVE = 'Never'
    Invoke-Tool $script:Git @('-C',$source,'fetch','--no-tags','origin',$Config.Branch) | Out-Null
    $commit = (Invoke-Tool $script:Git @('-C',$source,'rev-parse','FETCH_HEAD')).Trim()
    $old = if (Test-Path -LiteralPath $script:StatePath) { Read-Json $script:StatePath } else { $null }
    if ($old -and $old.Commit -eq $commit) { Write-Log "Already running $($commit.Substring(0,12)); no rebuild or restart."; return }
    if ($old) {
        $ancestor = Invoke-Tool $script:Git @('-C',$source,'merge-base','--is-ancestor',$old.Commit,$commit) -AllowFailure
        if ($ancestor.Code -ne 0) { throw 'Remote history rewound/diverged. Automatic deployment stopped; no force reset.' }
    }
    $release = Join-Path $script:InstallRoot "Releases\$commit"
    if (-not (Test-Path -LiteralPath $release)) {
        Invoke-Tool $script:Git @('-C',$source,'worktree','add','--detach',$release,$commit) | Out-Null
    } elseif ((Invoke-Tool $script:Git @('-C',$release,'status','--porcelain')).Trim()) {
        throw 'Candidate release has local changes; refusing to deploy it.'
    }
    $override = New-Override $Config $commit
    Test-ComposeSafety $Config $release $override
    Write-Log "Building candidate $($commit.Substring(0,12)); the running portal stays available during the build."
    $build = Invoke-Compose $Config $release $override @('build','backend','frontend')
    Add-Content -LiteralPath $script:LogFile -Value $build
    if ($Automatic -and $old) {
        # Evaluate after the build, immediately before any outage.
        $ready = Invoke-Maintenance $Config $release $override @('readiness')
        if (-not $ready.ready) { Write-Log $ready.reason; return }
    }
    $snapshot = $null
    $stopped = $false
    $exposed = $false
    try {
        $pending = @{Commit=$commit;Release=$release;Override=$override;Previous=$old;Snapshot=$null;Exposed=$false}
        Save-Json $script:PendingPath $pending
        Write-Log 'Switching versions: stopping services briefly and backing up learner records.'
        if ($old) { Invoke-Compose $Config $old.Release $old.Override @('stop','frontend','backend') | Out-Null }
        $stopped = $true
        $snapshot = Invoke-Maintenance $Config $release $override @('backup')
        $pending.Snapshot = $snapshot
        Save-Json $script:PendingPath $pending
        # Keep nginx stopped until the migrated database and old records are verified.
        Invoke-Compose $Config $release $override @('up','-d','--no-build','--wait','--wait-timeout',"$WaitSeconds",'backend') | Out-Null
        if (-not $snapshot.empty) {
            Invoke-Maintenance $Config $release $override @('verify','--snapshot',([IO.Path]::ChangeExtension($snapshot.backup,'.json'))) | Out-Null
        }
        $exposed = $true
        $pending.Exposed = $true
        Save-Json $script:PendingPath $pending
        Invoke-Compose $Config $release $override @('up','-d','--no-build','--wait','--wait-timeout',"$WaitSeconds",'frontend') | Out-Null
        $health = Invoke-RestMethod "http://127.0.0.1:$($Config.Port)/api/health" -TimeoutSec 15
        if ($health.status -ne 'ok' -or $health.database -ne 'ok') { throw 'Post-deployment health check failed.' }
        Complete-Release $commit $release $override
        Write-Log "Deployed $($commit.Substring(0,12)). Open http://localhost:$($Config.Port). Progress verified and retained."
    } catch {
        $failure = $_
        if ($stopped) {
            Write-Log 'Deployment failed. Stopping candidate services before recovery.'
            Invoke-Compose $Config $release $override @('stop','frontend','backend') | Out-Null
            if ($exposed) {
                Write-Log 'Frontend may have accepted new learner writes. Keeping the current database; no automatic database rollback. Rerun Update to retry this version.'
            } elseif ($snapshot -and -not $snapshot.empty) {
                Invoke-Maintenance $Config $release $override @('restore','--snapshot',$snapshot.backup) | Out-Null
            }
            if ($old -and -not $exposed) {
                Invoke-Compose $Config $old.Release $old.Override @('up','-d','--no-build','--wait','--wait-timeout',"$WaitSeconds") | Out-Null
                Write-Log 'Previous version restored. Failed database retained beside the pre-update backup.'
            }
            if (-not $exposed) { Archive-Pending }
        }
        throw $failure
    }
}

if ($LibraryOnly) { return }
$script:LogFile = $null
$script:InstallRoot = [IO.Path]::GetFullPath($Root)
if ($script:InstallRoot -match '["\r\n$#]') { throw 'Installation path contains unsupported dotenv characters.' }
if ($script:InstallRoot.TrimEnd('\') -eq [IO.Path]::GetPathRoot($script:InstallRoot).TrimEnd('\') -or
    (Test-Path -LiteralPath (Join-Path $script:InstallRoot '.git'))) {
    throw 'Choose a dedicated installation root outside any repository, not a drive root.'
}
$script:ConfigPath = Join-Path $script:InstallRoot 'install.json'
$script:StatePath = Join-Path $script:InstallRoot 'current.json'
$script:PendingPath = Join-Path $script:InstallRoot 'pending.json'
$lock = $null
try {
    New-Item -ItemType Directory -Force (Join-Path $script:InstallRoot 'Logs') | Out-Null
    $script:LogFile = Join-Path $script:InstallRoot 'Logs\deployment.log'
    $lock = [IO.File]::Open((Join-Path $script:InstallRoot 'Logs\update.lock'), 'OpenOrCreate','ReadWrite','None')
    if ($Action -notin @('EnableUpdates','DisableUpdates')) { Test-Requirements }
    if ($Action -eq 'Check') { return }
    if ($Action -eq 'Install') {
        if ($Repository -match '^https?://') {
            $repoUri = [uri]$Repository
            if ($repoUri.Scheme -ne 'https' -or $repoUri.UserInfo -or $repoUri.Query -or $repoUri.Fragment) {
                throw 'Use a plain HTTPS repository URL without embedded credentials, queries or fragments.'
            }
        }
        if (Test-Path -LiteralPath $script:StatePath) { throw 'Already installed. Use -Action Update.' }
        if ((Invoke-Tool $script:Docker @('ps','-aq','--filter',"label=com.docker.compose.project=$Project")).Trim()) {
            throw 'This Docker project name is already in use. Do not install over another running academy.'
        }
        if (-not $CoursesDirectory -or -not (Test-Path -LiteralPath $CoursesDirectory -PathType Container)) {
            throw 'Supply -CoursesDirectory pointing to the existing local Courses folder.'
        }
        $courses = (Resolve-Path -LiteralPath $CoursesDirectory).Path
        if ($courses -match '["\r\n$#]') { throw 'Course path contains unsupported dotenv characters.' }
        foreach ($name in @('Data','Releases')) { New-Item -ItemType Directory -Force (Join-Path $script:InstallRoot $name) | Out-Null }
        $data = Join-Path $script:InstallRoot 'Data'
        if ($SeedDatabase) {
            if (Test-Path -LiteralPath (Join-Path $data 'academy.sqlite3')) { throw 'Seed import is first-install only; existing learner data will not be overwritten.' }
            Copy-Item -LiteralPath $SeedDatabase -Destination (Join-Path $data 'academy.sqlite3')
        }
        $source = Join-Path $script:InstallRoot 'Source'
        if (-not (Test-Path -LiteralPath $source)) {
            Invoke-Tool $script:Git @('clone','--branch',$Branch,'--single-branch','--',$Repository,$source) | Out-Null
        } else {
            $origin = (Invoke-Tool $script:Git @('-C',$source,'remote','get-url','origin')).Trim()
            if ($origin.TrimEnd('/').Replace('.git','') -ne $Repository.TrimEnd('/').Replace('.git','')) { throw 'Existing Source origin differs from the requested repository.' }
        }
        $config = @{Repository=$Repository;Branch=$Branch;Courses=$courses;Data=$data;Port=$Port;Project=$Project}
        Save-Json $script:ConfigPath $config
        $environment = 'DATA_DIR="{0}"{2}COURSES_DIR="{1}"{2}' -f $data.Replace('\','/'),$courses.Replace('\','/'),[Environment]::NewLine
        [IO.File]::WriteAllText((Join-Path $script:InstallRoot 'academy.env'), $environment, [Text.UTF8Encoding]::new($false))
        Deploy-Version $config -FirstInstall
        if (-not $SkipAutoUpdates) { Register-Updates }
    } else {
        if (-not (Test-Path -LiteralPath $script:ConfigPath)) { throw 'No installation found at this Root. Run -Action Install first.' }
        $config = Read-Json $script:ConfigPath
        switch ($Action) {
            'Update' { Deploy-Version $config }
            'Backup' {
                $state = Read-Json $script:StatePath
                Invoke-Compose $config $state.Release $state.Override @('exec','-T','backend','python','-m','app.maintenance','backup') | Write-Host
            }
            'ImportGuide' {
                if (-not $GuideFile -or [IO.Path]::GetExtension($GuideFile) -ne '.json') { throw 'Supply -GuideFile pointing to a private authored guide JSON.' }
                $state = Read-Json $script:StatePath
                $imports = Join-Path $config.Data 'imports'
                New-Item -ItemType Directory -Force $imports | Out-Null
                $name = [guid]::NewGuid().ToString('N') + '.json'
                Copy-Item -LiteralPath $GuideFile -Destination (Join-Path $imports $name)
                Invoke-Compose $config $state.Release $state.Override @('exec','-T','backend','python','-m','app.guided',"/data/imports/$name") | Write-Host
                Write-Log 'Guide imported and published directly. Existing identities and earned XP retained. Refresh the portal.'
            }
            'EnableUpdates' { Register-Updates }
            'DisableUpdates' { Disable-ScheduledTask -TaskName "$($config.Project)-updates" | Out-Null; Write-Log 'Automatic updates disabled; installed portal and progress retained.' }
            'Status' {
                $state = Read-Json $script:StatePath
                Write-Log "Installed commit: $($state.Commit); branch: $($config.Branch); data: $($config.Data)"
                Invoke-Compose $config $state.Release $state.Override @('ps') | Write-Host
                $task = Get-ScheduledTask -TaskName "$($config.Project)-updates" -ErrorAction SilentlyContinue
                Write-Log $(if ($task) { "Scheduled updates: $($task.State)" } else { 'Scheduled updates: not registered' })
            }
        }
    }
} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    Write-Log 'No prerequisites were silently installed. For missing Docker/WSL/Git, follow docs/LAPTOP_DEPLOYMENT.md and rerun.'
    exit 1
} finally {
    if ($lock) { $lock.Dispose() }
}
