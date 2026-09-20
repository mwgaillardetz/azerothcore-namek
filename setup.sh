#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
server_root="$repo_root/azerothcore-wotlk"
runtime_root="$repo_root/runtime"
core_revision=$(tr -d '[:space:]' < "$repo_root/core-revision.txt")

skip_build=false
if [[ ${1:-} == --skip-build && $# == 1 ]]; then
    skip_build=true
elif (( $# )); then
    echo "Usage: $0 [--skip-build]" >&2
    exit 2
fi

for command in git docker python3; do
    command -v "$command" >/dev/null || { echo "$command is required" >&2; exit 1; }
done
docker compose version >/dev/null

if [[ ! -d "$server_root" ]]; then
    git clone --branch Playerbot https://github.com/liyunfan1223/azerothcore-wotlk.git "$server_root"
    git -C "$server_root" checkout --detach "$core_revision"
fi
actual_revision=$(git -C "$server_root" rev-parse HEAD)
if [[ "$actual_revision" != "$core_revision" ]]; then
    echo "Core checkout is at $actual_revision, expected $core_revision. Preserve local changes and align the checkout before running setup." >&2
    exit 1
fi

mkdir -p "$runtime_root/etc" "$runtime_root/logs"
cp -an "$repo_root/config/." "$runtime_root/etc/"
cp -a "$repo_root/modules/." "$server_root/modules/"
cp "$repo_root/docker/docker-compose.yml" "$server_root/docker-compose.yml"
cp "$repo_root/docker/Dockerfile" "$server_root/apps/docker/Dockerfile"
cp "$repo_root/docker/Dockerfile.llm-chatter" "$server_root/apps/docker/Dockerfile.llm-chatter"

if [[ -f "$repo_root/.env" ]]; then
    cp "$repo_root/.env" "$server_root/.env"
elif [[ ! -f "$server_root/.env" ]]; then
    cp "$repo_root/.env.example" "$server_root/.env"
    echo "Edit $server_root/.env and change DOCKER_DB_ROOT_PASSWORD before exposing the server." >&2
fi

for sql_file in "$repo_root"/sql/world/*.sql; do
    [[ -e "$sql_file" ]] || continue
    cp "$sql_file" "$server_root/data/sql/updates/pending_db_world/namek_$(basename "$sql_file")"
done

if [[ "$skip_build" == false ]]; then
    docker compose --project-directory "$server_root" config --quiet
    docker compose --project-directory "$server_root" build ac-worldserver ac-authserver ac-db-import ac-llm-chatter-bridge
    python3 "$repo_root/tools/verify-runtime.py" --image namek/worldserver:local
    docker compose --project-directory "$server_root" up -d --no-build
    deadline=$((SECONDS + 600))
    until [[ $(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' ac-worldserver) == healthy ]]; do
        if (( SECONDS >= deadline )); then
            echo 'Worldserver did not become healthy within 10 minutes; inspect docker compose logs.' >&2
            exit 1
        fi
        sleep 5
    done
    python3 "$repo_root/tools/verify-runtime.py"
fi

echo "Namek setup is ready in $server_root"
