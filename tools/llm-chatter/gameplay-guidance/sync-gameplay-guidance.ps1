param(
    [ValidateSet('Check', 'Install', 'Capture')]
    [string]$Mode = 'Check',
    [string]$ProjectRoot = 'C:\docker-projects\azeroth-core-coconut\AzerothCore-with-Playerbots-Docker-Setup\azerothcore-wotlk'
)

$ErrorActionPreference = 'Stop'
$archiveRoot = $PSScriptRoot
$archiveModules = Join-Path $archiveRoot 'module-files'
$archiveTests = Join-Path $archiveRoot 'tests'
$liveTools = Join-Path $ProjectRoot 'modules\mod-llm-chatter\tools'
$liveTests = Join-Path $liveTools 'tests'

if (-not (Test-Path -LiteralPath $liveTools -PathType Container)) {
    throw "AzerothCore tools directory not found: $liveTools"
}

$moduleNames = @(
    'chatter_constants.py',
    'chatter_gameplay_knowledge.py',
    'chatter_shared.py',
    'chatter_general.py',
    'chatter_proximity.py',
    'chatter_group.py',
    'chatter_group_handlers.py',
    'chatter_group_prompts.py',
    'chatter_guild_player.py',
    'llm_chatter_bridge.py'
)
$testNames = @(
    'test_gameplay_knowledge.py',
    'test_hybrid_chatter_mode.py',
    'test_human_topic_separation.py'
)

function Copy-ExactFile {
    param([string]$Source, [string]$Destination)
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        throw "Required source file not found: $Source"
    }
    Copy-Item -LiteralPath $Source -Destination $Destination -Force
}

if ($Mode -eq 'Install') {
    foreach ($name in $moduleNames) {
        Copy-ExactFile (Join-Path $archiveModules $name) (Join-Path $liveTools $name)
    }
    foreach ($name in $testNames) {
        Copy-ExactFile (Join-Path $archiveTests $name) (Join-Path $liveTests $name)
    }
    Write-Host 'Installed archived gameplay-guidance files. Restart ac-llm-chatter-bridge to load them.'
    exit 0
}

if ($Mode -eq 'Capture') {
    foreach ($name in $moduleNames) {
        Copy-ExactFile (Join-Path $liveTools $name) (Join-Path $archiveModules $name)
    }
    foreach ($name in $testNames) {
        Copy-ExactFile (Join-Path $liveTests $name) (Join-Path $archiveTests $name)
    }
    Write-Host 'Captured live gameplay-guidance files into this repository.'
    exit 0
}

$different = $false
foreach ($name in $moduleNames) {
    $archive = Join-Path $archiveModules $name
    $live = Join-Path $liveTools $name
    $matches = (
        (Test-Path -LiteralPath $archive -PathType Leaf) -and
        (Test-Path -LiteralPath $live -PathType Leaf) -and
        ((Get-FileHash -LiteralPath $archive).Hash -eq (Get-FileHash -LiteralPath $live).Hash)
    )
    Write-Host ("{0,-40} {1}" -f $name, $(if ($matches) { 'MATCH' } else { 'DIFFERENT' }))
    if (-not $matches) { $different = $true }
}
foreach ($name in $testNames) {
    $archive = Join-Path $archiveTests $name
    $live = Join-Path $liveTests $name
    $matches = (
        (Test-Path -LiteralPath $archive -PathType Leaf) -and
        (Test-Path -LiteralPath $live -PathType Leaf) -and
        ((Get-FileHash -LiteralPath $archive).Hash -eq (Get-FileHash -LiteralPath $live).Hash)
    )
    Write-Host ("tests/{0,-34} {1}" -f $name, $(if ($matches) { 'MATCH' } else { 'DIFFERENT' }))
    if (-not $matches) { $different = $true }
}

if ($different) { exit 1 }
Write-Host 'Archive matches the live implementation.'
