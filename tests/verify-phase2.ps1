param([string]$Origin = 'http://localhost:3001')
$ErrorActionPreference = 'Stop'
$composeFiles = @('-p', 'unreal-academy-verification', '-f', 'compose.yaml', '-f', 'tests/compose.verification.yaml')
$page = Invoke-WebRequest $Origin -UseBasicParsing
if ($page.StatusCode -ne 200) { throw 'Frontend failed' }
$health = Invoke-RestMethod "$Origin/api/health"
if ($health.phase -ne 2 -or $health.database -ne 'ok') { throw 'Health failed' }
$import = Invoke-RestMethod "$Origin/api/courses/import" -Method Post -ContentType 'application/json' -Body '{"folder":"Verification Course"}'
$course = Invoke-RestMethod "$Origin/api/courses/$($import.course_id)"
$lesson = $course.lessons[0]
if (-not $lesson.playable) { throw 'Generated video format check failed' }
$rangeRequest = [System.Net.HttpWebRequest]::Create("$Origin/api/lessons/$($lesson.id)/video")
$rangeRequest.AddRange(0, 99)
$rangeResponse = $rangeRequest.GetResponse()
try {
    if ([int]$rangeResponse.StatusCode -ne 206 -or $rangeResponse.ContentLength -ne 100) { throw 'Video range failed' }
} finally { $rangeResponse.Close() }
$captions = Invoke-WebRequest "$Origin/api/lessons/$($lesson.id)/captions" -UseBasicParsing
if (-not $captions.Content.StartsWith('WEBVTT')) { throw 'Captions failed' }
$resource = Invoke-WebRequest "$Origin/api/resources/$($course.resources[0].id)/download" -UseBasicParsing
if ($resource.StatusCode -ne 200 -or $resource.Headers['Content-Disposition'] -notmatch 'attachment') { throw 'Download failed' }
Invoke-RestMethod "$Origin/api/lessons/$($lesson.id)/progress" -Method Put -ContentType 'application/json' -Body '{"position":1.5,"watched":true}' | Out-Null
docker compose @composeFiles restart backend
if ($LASTEXITCODE -ne 0) { throw 'Restart failed' }
docker compose @composeFiles up -d --wait
if ($LASTEXITCODE -ne 0) { throw 'Readiness failed' }
$rescan = Invoke-RestMethod "$Origin/api/courses/import" -Method Post -ContentType 'application/json' -Body '{"folder":"Verification Course"}'
if ($rescan.course_id -ne $import.course_id) { throw 'Course duplicated on rescan' }
$course = Invoke-RestMethod "$Origin/api/courses/$($import.course_id)"
if ($course.lessons.Count -ne 1 -or $course.lessons[0].id -ne $lesson.id -or $course.lessons[0].position -ne 1.5 -or $course.lessons[0].watched -ne 1) {
    throw 'Lesson identity or progress persistence failed'
}
docker compose @composeFiles up -d --force-recreate --no-deps backend
if ($LASTEXITCODE -ne 0) { throw 'Container replacement failed' }
docker compose @composeFiles up -d --wait
if ($LASTEXITCODE -ne 0) { throw 'Replacement readiness failed' }
$course = Invoke-RestMethod "$Origin/api/courses/$($import.course_id)"
if ($course.lessons[0].position -ne 1.5 -or $course.lessons[0].watched -ne 1) { throw 'Replacement persistence failed' }
Write-Output 'PASS: same-origin course import/rescan, ranged video, captions, resource download, and progress after container restart/replacement'
