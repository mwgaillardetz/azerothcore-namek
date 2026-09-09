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
    docker compose --project-directory $serverRoot up -d --build
}

Write-Host "Namek setup is ready in $serverRoot"
