param(
    [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'
$repoRoot = $PSScriptRoot
$serverRoot = Join-Path $repoRoot 'azerothcore-wotlk'
$runtimeRoot = Join-Path $repoRoot 'runtime'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is required.'
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker Desktop is required.'
}

if (-not (Test-Path -LiteralPath $serverRoot)) {
    git clone --branch Playerbot https://github.com/liyunfan1223/azerothcore-wotlk.git $serverRoot
}

New-Item -ItemType Directory -Force -Path (Join-Path $runtimeRoot 'etc'), (Join-Path $runtimeRoot 'logs') | Out-Null
Copy-Item -Path (Join-Path $repoRoot 'config\*') -Destination (Join-Path $runtimeRoot 'etc') -Recurse -Force
Copy-Item -Path (Join-Path $repoRoot 'modules\*') -Destination (Join-Path $serverRoot 'modules') -Recurse -Force
Copy-Item -LiteralPath (Join-Path $repoRoot 'docker\docker-compose.yml') -Destination $serverRoot -Force

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
    docker compose --project-directory $serverRoot up -d --build
}

Write-Host "Namek setup is ready in $serverRoot"
