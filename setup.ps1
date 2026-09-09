param(
    [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'
$repoRoot = $PSScriptRoot
$serverRoot = Join-Path $repoRoot 'azerothcore-wotlk'
$runtimeRoot = Join-Path $repoRoot 'runtime'
$coreRevision = (Get-Content -LiteralPath (Join-Path $repoRoot 'core-revision.txt') -Raw).Trim()

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is required.'
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker Desktop is required.'
}

if (-not (Test-Path -LiteralPath $serverRoot)) {
    git clone --branch Playerbot https://github.com/liyunfan1223/azerothcore-wotlk.git $serverRoot
    if ($LASTEXITCODE -ne 0) { throw 'AzerothCore clone failed; setup stopped.' }
    git -C $serverRoot checkout --detach $coreRevision
    if ($LASTEXITCODE -ne 0) { throw 'Could not check out the pinned core revision; setup stopped.' }
}
$actualRevision = git -C $serverRoot rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'Could not inspect the existing core checkout.' }
if ($actualRevision -ne $coreRevision) {
    throw "Core checkout is at $actualRevision, expected $coreRevision. Preserve local changes and align the checkout before running setup."
}

New-Item -ItemType Directory -Force -Path (Join-Path $runtimeRoot 'etc'), (Join-Path $runtimeRoot 'logs') | Out-Null
$configRoot = Join-Path $repoRoot 'config'
Get-ChildItem -LiteralPath $configRoot -Recurse -File | ForEach-Object {
    $relativePath = $_.FullName.Substring($configRoot.Length + 1)
    $destination = Join-Path (Join-Path $runtimeRoot 'etc') $relativePath
    if (-not (Test-Path -LiteralPath $destination)) {
        New-Item -ItemType Directory -Force -Path (Split-Path $destination -Parent) | Out-Null
        Copy-Item -LiteralPath $_.FullName -Destination $destination
    }
}
Copy-Item -Path (Join-Path $repoRoot 'modules\*') -Destination (Join-Path $serverRoot 'modules') -Recurse -Force
Copy-Item -LiteralPath (Join-Path $repoRoot 'docker\docker-compose.yml') -Destination $serverRoot -Force
Copy-Item -LiteralPath (Join-Path $repoRoot 'docker\Dockerfile') -Destination (Join-Path $serverRoot 'apps\docker\Dockerfile') -Force
Copy-Item -LiteralPath (Join-Path $repoRoot 'docker\Dockerfile.llm-chatter') -Destination (Join-Path $serverRoot 'apps\docker\Dockerfile.llm-chatter') -Force

$envFile = Join-Path $serverRoot '.env'
$privateEnvFile = Join-Path $repoRoot '.env'
if (Test-Path -LiteralPath $privateEnvFile) {
    Copy-Item -LiteralPath $privateEnvFile -Destination $envFile -Force
} elseif (-not (Test-Path -LiteralPath $envFile)) {
    Copy-Item -LiteralPath (Join-Path $repoRoot '.env.example') -Destination $envFile
    Write-Warning "Edit $envFile and change DOCKER_DB_ROOT_PASSWORD before exposing the server."
}

Get-ChildItem -LiteralPath (Join-Path $repoRoot 'sql\world') -Filter '*.sql' | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $serverRoot "data\sql\updates\pending_db_world\namek_$($_.Name)") -Force
}

if (-not $SkipBuild) {
    docker compose --project-directory $serverRoot config --quiet
    if ($LASTEXITCODE -ne 0) { throw 'Compose validation failed; setup stopped.' }
    docker compose --project-directory $serverRoot build ac-worldserver ac-authserver ac-db-import ac-llm-chatter-bridge
    if ($LASTEXITCODE -ne 0) { throw 'Custom image build failed; existing containers were not replaced.' }
    $expectedConfigs = @('playerbots.conf.dist', 'mod_llm_chatter.conf.dist')
    $expectedConfigs += Get-ChildItem -LiteralPath (Join-Path $repoRoot 'modules') -Recurse -Filter '*.conf.dist' |
        ForEach-Object { $_.Name }
    $expectedConfigs = $expectedConfigs | Sort-Object -Unique
    $installedConfigs = docker run --rm --entrypoint ls namek/worldserver:local -1 /azerothcore/env/ref/etc/modules
    if ($LASTEXITCODE -ne 0) { throw 'Could not inspect built image; deployment stopped.' }
    foreach ($configName in $expectedConfigs) {
        if ($installedConfigs -notcontains $configName) {
            throw "Built image is missing $configName; deployment stopped."
        }
    }
    docker compose --project-directory $serverRoot up -d --no-build
    if ($LASTEXITCODE -ne 0) { throw 'Stack startup failed; inspect docker compose logs.' }
    $deadline = (Get-Date).AddMinutes(10)
    do {
        $health = docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' ac-worldserver
        if ($LASTEXITCODE -ne 0) { throw 'Could not inspect worldserver startup.' }
        if ($health -eq 'healthy') { break }
        if ($health -in @('unhealthy', 'exited', 'dead', 'restarting')) {
            throw "Worldserver startup failed ($health); inspect its logs."
        }
        Start-Sleep -Seconds 5
    } while ((Get-Date) -lt $deadline)
    if ($health -ne 'healthy') { throw 'Worldserver did not become healthy within 10 minutes.' }
    $startupErrors = docker exec ac-worldserver cat /azerothcore/env/dist/logs/Errors.log
    if ($LASTEXITCODE -ne 0) { throw 'Could not read worldserver startup errors.' }
    if ($startupErrors -match 'assigned in the database, but has no code') {
        throw 'The database references missing scripts; core/database versions need to be aligned.'
    }
}

Write-Host "Namek setup is ready in $serverRoot"
