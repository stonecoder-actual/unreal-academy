# Run only against the isolated snapshot on port 3002, never the real learner.
$ErrorActionPreference='Stop'
$origin='http://localhost:3002'
$guides=Invoke-RestMethod "$origin/api/parent/guides"
$guide=$guides | Select-Object -First 1
if (-not $guide) { throw 'Load a guide into the isolated snapshot first' }
if ($guide.status -eq 'draft') {
    Invoke-RestMethod "$origin/api/parent/guides/$($guide.id)/publish" -Method Post | Out-Null
}
$maximum=0
foreach ($question in $guide.document.questions) {
    $body=@{answer=$question.options[$question.correct]} | ConvertTo-Json
    $url="$origin/api/guides/$($guide.id)/questions/$($question.id)/answer"
    $result=Invoke-RestMethod $url -Method Post -ContentType 'application/json' -Body $body
    if (-not $result.correct) { throw 'A canonical answer was rejected' }
    $repeat=Invoke-RestMethod $url -Method Post -ContentType 'application/json' -Body $body
    if ($repeat.awarded_xp -ne 0) { throw 'Repeated answer earned XP' }
    $maximum += $question.xp
}
$student=Invoke-RestMethod "$origin/api/lessons/$($guide.document.lesson_id)/guide"
$xp=Invoke-RestMethod "$origin/api/xp"
$expected=$maximum
if ($student.submission -and $student.submission.status -eq 'approved') { $expected += $guide.document.practice.xp }
if ($xp.total_xp -ne $expected -or $xp.level -ne 2) { throw 'XP total or level boundary failed' }
if ($student.solved.Count -ne $guide.document.questions.Count) { throw 'Saved quiz state failed' }
if (-not $student.submission) {
    $evidence=@{
        prediction='AUTOMATED TEST ONLY: a child component should follow its parent.'
        observation='AUTOMATED TEST ONLY: this text tests the submission interface; no Unreal exercise was performed.'
        explanation='AUTOMATED TEST ONLY: practical evidence requires a real parent inspection in normal use.'
    } | ConvertTo-Json
    $submission=Invoke-RestMethod "$origin/api/guides/$($guide.id)/practice" -Method Post -ContentType 'application/json' -Body $evidence
    if ($submission.awarded_xp -ne 0) { throw 'Submitting practice alone earned XP' }
}
Write-Output "PASS: $($guide.document.questions.Count) correct checks, $maximum quiz XP, $($xp.total_xp) total XP, Level $($xp.level), repeat answers earn zero."
