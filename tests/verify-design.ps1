# Read-only smoke checks for the live app; reward tests use the isolated 3004 app.
$ErrorActionPreference = 'Stop'
$origin = 'http://localhost:3000'
$health = Invoke-RestMethod "$origin/api/health"
if ($health.status -ne 'ok') { throw 'Backend health failed' }
$page = Invoke-WebRequest $origin -UseBasicParsing
if ($page.StatusCode -ne 200) { throw 'Frontend did not load' }
$asset = [regex]::Match($page.Content, 'src="([^"]+\.js)"').Groups[1].Value
$bundle = (Invoke-WebRequest ($origin + $asset) -UseBasicParsing).Content
if ($bundle.Contains('Progression design studio') -or $bundle.Contains('Responsive academy preview')) {
    throw 'Development-only demonstrations leaked into the production bundle'
}
$courses = Invoke-RestMethod "$origin/api/courses"
$localCount=0
$externalCount=0
foreach ($course in $courses) {
    $detail = Invoke-RestMethod "$origin/api/courses/$($course.id)"
    if ($course.source_type -eq 'udemy') {
        foreach ($item in $detail.lessons) {
            if ($item.external_url -notmatch '^https://www\.udemy\.com/course/[a-z0-9-]+/learn/(lecture|quiz)/[0-9]+$') { throw 'Invalid external lesson link' }
        }
        $externalCount++
        continue
    }
    $localCount++
    $lesson = $detail.lessons | Where-Object { $_.available -and $_.playable } | Select-Object -First 1
    if (-not $lesson) { throw "No playable lesson in $($course.title)" }
    $rangeRequest = [System.Net.HttpWebRequest]::Create("$origin/api/lessons/$($lesson.id)/video")
    $rangeRequest.AddRange(0,99)
    $rangeResponse = $rangeRequest.GetResponse()
    try { if ([int]$rangeResponse.StatusCode -ne 206 -or $rangeResponse.ContentLength -ne 100) { throw 'Video range failed' } }
    finally { $rangeResponse.Close() }
    if ($lesson.caption_path) {
        $caption = Invoke-WebRequest "$origin/api/lessons/$($lesson.id)/captions" -UseBasicParsing
        if (-not $caption.Content.StartsWith('WEBVTT')) { throw 'Caption response failed' }
    }
}
Write-Output "Live frontend, health, $localCount local course video ranges/captions, $externalCount external course link inventories, and production preview exclusion passed."
