$ErrorActionPreference = 'Stop'
$origin = 'http://localhost:3000'

function Assert-Healthy {
    $health = Invoke-RestMethod "$origin/api/health"
    if ($health.status -ne 'ok' -or $health.database -ne 'ok') {
        throw 'API or database is unhealthy'
    }
}

Assert-Healthy
$page = Invoke-WebRequest $origin -UseBasicParsing
if ($page.StatusCode -ne 200 -or -not $page.Content.Contains('Unreal Academy')) {
    throw 'Frontend verification failed'
}
$original = (Invoke-RestMethod "$origin/api/settings").welcome_message
$marker = "Persistence verified $([guid]::NewGuid())"
try {
    $body = @{ welcome_message = $marker } | ConvertTo-Json
    $saved = Invoke-RestMethod "$origin/api/settings" -Method Put -ContentType 'application/json' -Body $body
    if ($saved.welcome_message -ne $marker) { throw 'Write verification failed' }
    docker compose restart backend
    if ($LASTEXITCODE -ne 0) { throw 'Container restart failed' }
    docker compose up -d --wait
    if ($LASTEXITCODE -ne 0) { throw 'Container readiness failed' }
    Assert-Healthy
    if ((Invoke-RestMethod "$origin/api/settings").welcome_message -ne $marker) {
        throw 'Database persistence verification failed'
    }
    Write-Output 'PASS: frontend HTTP 200, same-origin API, SQLite read/write and container restart persistence'
} finally {
    $body = @{ welcome_message = $original } | ConvertTo-Json
    Invoke-RestMethod "$origin/api/settings" -Method Put -ContentType 'application/json' -Body $body | Out-Null
}
