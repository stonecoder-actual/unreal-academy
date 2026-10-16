# Real Git + Docker integration, isolated from Jaxon's data. No external Git push.
# Run from a checkout with Docker Desktop available. Fixtures are retained for inspection.
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$fixture = Join-Path $env:TEMP ('Unreal Academy deploy test ' + [guid]::NewGuid().ToString('N'))
$seed = Join-Path $fixture 'Git origin'
$install = Join-Path $fixture 'Laptop'
$courses = Join-Path $fixture 'Courses'
$project = 'ua-deploy-test-' + [guid]::NewGuid().ToString('N').Substring(0,8)
$listener = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,0)
$listener.Start(); $port = $listener.LocalEndpoint.Port; $listener.Stop()
$origin = "http://127.0.0.1:$port"
$powershell = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
New-Item -ItemType Directory -Force $seed,$courses | Out-Null
function Native($Tool,[string[]]$Arguments) {
    & $Tool @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Tool failed ($LASTEXITCODE)" }
}
function Assert($Condition,$Message) { if (-not $Condition) { throw $Message } }
function Update([switch]$ExpectFailure,[switch]$Auto) {
    $arguments = @('-NoProfile','-ExecutionPolicy','Bypass','-File',(Join-Path $repo 'scripts\Academy.ps1'),'-Action','Update','-Root',$install,'-WaitSeconds','30')
    if ($Auto) { $arguments += '-Automatic' }
    & $powershell @arguments
    if ($ExpectFailure) { Assert ($LASTEXITCODE -ne 0) 'Expected update refusal/failure' }
    else { Assert ($LASTEXITCODE -eq 0) 'Update failed' }
}
function Commit([string]$Message) {
    Native git @('-C',$seed,'add','.')
    Native git @('-C',$seed,'commit','-q','-m',$Message)
}
function Assert-Saved {
    Assert ((Invoke-RestMethod "$origin/api/xp").total_xp -eq 5) 'Earned XP changed'
    Assert ((Invoke-RestMethod "$origin/api/settings").welcome_message -eq 'Deployment test sentinel') 'Setting changed'
    $lesson = (Invoke-RestMethod "$origin/api/courses/$script:CourseId").lessons[0]
    Assert ($lesson.watched -eq 1 -and $lesson.position -eq 18) 'Playback progress changed'
}
try {
    # Copy only Git-visible application inputs; never data, course files or .env.
    $files = & git -C $repo ls-files -co --exclude-standard backend frontend scripts compose.yaml
    foreach ($file in $files) {
        if (-not (Test-Path -LiteralPath (Join-Path $repo $file) -PathType Leaf)) { continue }
        $target = Join-Path $seed $file
        New-Item -ItemType Directory -Force (Split-Path $target) | Out-Null
        Copy-Item -LiteralPath (Join-Path $repo $file) -Destination $target
    }
    Native git @('-C',$seed,'init','-q','-b','main')
    Native git @('-C',$seed,'config','core.autocrlf','false')
    Native git @('-C',$seed,'config','user.name','Deployment test')
    Native git @('-C',$seed,'config','user.email','deployment@example.invalid')
    Commit 'Synthetic deployment fixture'
    Native $powershell @('-NoProfile','-ExecutionPolicy','Bypass','-File',(Join-Path $repo 'scripts\Academy.ps1'),'-Action','Install','-Root',$install,'-Repository',$seed,'-CoursesDirectory',$courses,'-Port',"$port",'-Project',$project,'-SkipAutoUpdates','-WaitSeconds','30')
    $manifest = @{slug='deployment-test';title='Synthetic deployment course';url='https://www.udemy.com/course/deployment-test/';difficulty='Beginner';lessons=@(@{external_id='123';title='Synthetic lesson';kind='video';section='Test';url='https://www.udemy.com/course/deployment-test/learn/lecture/123';duration=120;transcript=@{cues=@('Synthetic test only.');captured_at='2026-10-16T00:00:00Z'}})}
    $script:CourseId = (Invoke-RestMethod "$origin/api/parent/external-courses/import" -Method Post -ContentType application/json -Body ($manifest|ConvertTo-Json -Depth 8)).course_id
    $lessonId = (Invoke-RestMethod "$origin/api/courses/$script:CourseId").lessons[0].id
    $guide = @{lesson_id=$lessonId;title='Synthetic mission';overview='Deployment fixture only.';prerequisites=@();objectives=@('Test persistence');corrections=@();references=@();practice=$null;sections=@(@{id='test';title='Test';start=$null;end=$null;objective='Test';notes=@();pause_prompt='Think'});questions=@(@{id='check';section='test';prompt='Which synthetic answer is correct?';options=@('Correct','Incorrect');correct=0;explanation='Synthetic explanation';hint='Synthetic hint';xp=5})}
    $guide['takeaways']=@('Understand this synthetic transcript idea.')
    $guide.questions += @(1,2 | ForEach-Object { @{id="check-$_";section='test';prompt='Which synthetic answer is correct?';options=@('Correct','Incorrect');correct=0;explanation='Synthetic explanation';hint='Synthetic hint';xp=5} })
    $guide | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $install 'Data\fixture-guide.json') -Encoding UTF8
    Native $powershell @('-NoProfile','-ExecutionPolicy','Bypass','-File',(Join-Path $repo 'scripts\Academy.ps1'),'-Action','ImportGuide','-Root',$install,'-GuideFile',(Join-Path $install 'Data\fixture-guide.json'))
    $guideId = (Invoke-RestMethod "$origin/api/guided-lessons")[0].id
    Invoke-RestMethod "$origin/api/guides/$guideId/questions/check/answer" -Method Post -ContentType application/json -Body '{"answer":"Correct"}' | Out-Null
    Invoke-RestMethod "$origin/api/lessons/$lessonId/progress" -Method Put -ContentType application/json -Body '{"position":18,"watched":true}' | Out-Null
    Invoke-RestMethod "$origin/api/settings" -Method Put -ContentType application/json -Body '{"welcome_message":"Deployment test sentinel"}' | Out-Null
    $before = Get-Content (Join-Path $install 'current.json') -Raw | ConvertFrom-Json
    Set-Content -LiteralPath (Join-Path $seed 'release-marker.txt') -Value 'Second release'
    Commit 'Second synthetic release'
    Update -Auto
    Assert ((Get-Content (Join-Path $install 'current.json') -Raw | ConvertFrom-Json).Commit -eq $before.Commit) 'Automatic update ignored recent learning'
    Update
    Assert-Saved
    $current = Get-Content (Join-Path $install 'current.json') -Raw | ConvertFrom-Json
    Assert ($current.Commit -ne $before.Commit) 'Remote commit was not deployed'
    $container = (& docker inspect --format '{{.Id}}' "$project-backend-1").Trim()
    Update
    Assert ((& docker inspect --format '{{.Id}}' "$project-backend-1").Trim() -eq $container) 'No-change check restarted the app'
    $sourceCompose = Join-Path $install 'Source\compose.yaml'
    $originalCompose = [IO.File]::ReadAllText($sourceCompose)
    [IO.File]::AppendAllText($sourceCompose,"`n# synthetic local edit`n")
    Update -ExpectFailure
    [IO.File]::WriteAllText($sourceCompose,$originalCompose)
    $snapshot = Get-ChildItem (Join-Path $install 'Data\backups\deployments') -Filter '*.sqlite3' | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    $pending = @{Commit=$current.Commit;Release=$current.Release;Override=$current.Override;Previous=$current;Snapshot=@{empty=$false;backup=('/data/backups/deployments/'+$snapshot.Name)};Exposed=$false}
    Native docker @('stop',"$project-frontend-1","$project-backend-1")
    $pending | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $install 'pending.json') -Encoding UTF8
    Native git @('-C',(Join-Path $install 'Source'),'remote','set-url','origin',(Join-Path $fixture 'Unavailable remote'))
    Update -ExpectFailure
    Assert (-not (Test-Path (Join-Path $install 'pending.json'))) 'Interrupted update recovery did not finish before offline Git fetch'
    Native git @('-C',(Join-Path $install 'Source'),'remote','set-url','origin',$seed)
    Assert-Saved
    # After frontend exposure, recovery must keep writes newer than the snapshot.
    $pending.Exposed = $true
    $pending | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $install 'pending.json') -Encoding UTF8
    Invoke-RestMethod "$origin/api/settings" -Method Put -ContentType application/json -Body '{"welcome_message":"Writes after frontend exposure"}' | Out-Null
    Update
    Assert ((Invoke-RestMethod "$origin/api/settings").welcome_message -eq 'Writes after frontend exposure') 'Post-exposure recovery discarded newer writes'
    Invoke-RestMethod "$origin/api/settings" -Method Put -ContentType application/json -Body '{"welcome_message":"Deployment test sentinel"}' | Out-Null
    # A valid Git release with a deliberately broken backend exercises real recovery.
    Add-Content -LiteralPath (Join-Path $seed 'backend\app\main.py') -Value "`nraise RuntimeError('Synthetic deployment failure')"
    Commit 'Deliberately failing synthetic release'
    Update -ExpectFailure
    Assert-Saved
    Assert ((Get-Content (Join-Path $install 'current.json') -Raw | ConvertFrom-Json).Commit -eq $current.Commit) 'Failed release replaced known-good state'
    Assert (@(Get-ChildItem (Join-Path $install 'Data\backups\deployments') -Directory -Filter 'failed-*').Count -gt 0) 'Failed database was not preserved'
    Write-Host "PASS: fresh install, recent-activity deferral, Git update, no-op, dirty/offline refusal, interrupted-update recovery, post-exposure writes, health-failure rollback and unchanged XP/playback. Fixtures: $fixture"
} finally {
    # Stop only this unique disposable stack. Retain its database, releases and logs.
    $statePath = Join-Path $install 'current.json'
    if (Test-Path -LiteralPath $statePath) {
        $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
        & docker compose --project-name $project --project-directory $state.Release --env-file (Join-Path $install 'academy.env') -f (Join-Path $state.Release 'compose.yaml') -f $state.Override stop
    }
}
