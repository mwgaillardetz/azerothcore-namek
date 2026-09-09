# azerothcore-namek

<img src="https://static.wikia.nocookie.net/dragonball/images/4/43/NamekGreenPlanet.png/revision/latest/thumbnail/width/360/height/360?cb=20100731172310" alt="Planet Namek" width="110">

A custom containerized rendition of World of Warcraft - Wrath of the Litch King (3.3.5a). It includes Playerbots, my module collection, server configuration, low-level bot mounts, and a 24-slot bag for every newly created character.

## Server setup

I run this with Docker Desktop on Windows (I know 😞).

1. Install Git and Docker Desktop.
2. Clone this repository.
3. Copy `.env.example` to `.env`, choose a database password, and keep `.env` private.
4. Run `powershell -ExecutionPolicy Bypass -File .\setup.ps1` from the repository folder.
5. Wait for the database import and worldserver build to finish.
6. Create an account from the worldserver console:

```text
account create USERNAME PASSWORD
account set gmlevel USERNAME 3 -1
```

The active configuration is under `runtime\etc` after setup. The server listens on ports `3724` and `8085` by default.

Custom server images use `namek/*:local` and cannot be pulled from the upstream
registry. See [migration and recovery checks](docker/MIGRATION.md) before moving
the stack. Set `DOCKER_BUILD_JOBS` in `.env` to control build concurrency.

## Included modules

| Module | What I use it for |
| --- | --- |
| `mod-playerbots` | Random and account-controlled player bots |
| `mod-llm-chatter` | LLM-driven bot conversations and persistent identities |
| `mod-assistant` | In-game assistant features |
| `mod-aoe-loot` | Area-of-effect looting |
| `mod-ah-bot-plus` | Populated and managed auction house |
| `mod-arac` | Expanded race and class combinations |
| `mod-auto-revive` | Automatic player revival |
| `mod-fireworks-on-level` | Fireworks when a character levels |
| `mod-guildhouse` | Guild housing |
| `mod-learnspells` | Automatic spell learning, including my custom behavior |
| `mod-morphsummon` | Morph and summon commands |
| `mod-npc-all-mounts` | NPC access to the mount collection |
| `mod-npc-beastmaster` | Hunter-pet management NPC |
| `mod-npc-enchanter` | Enchanting NPC |
| `mod-npc-free-professions` | Free profession training NPC |
| `mod-npc-gambler` | Gambling NPC |
| `mod-premium` | Premium-account features |
| `mod-reagent-bank` | Reagent storage |
| `mod-solocraft` | Solo-friendly dungeon and raid scaling |
| `mod-transmog` | Transmogrification |
| `mod-ale` | AzerothCore Lua Engine support |

## LLM chatter bridge

`docker/docker-compose.yml` includes `ac-llm-chatter-bridge`, the Python worker
that turns server events into bot dialogue. Setup copies its Dockerfile into
the server checkout and uses the module sources already saved in this repository.
The service restarts automatically with Docker and keeps reports in a named volume.

For a fresh setup, first run `setup.ps1 -SkipBuild` to prepare the files. Edit
`runtime/etc/modules/mod_llm_chatter.conf` locally and fill in:

```ini
LLMChatter.Provider = openai
LLMChatter.Model = gpt-4o-mini
LLMChatter.OpenAI.ApiKey = YOUR_FULL_OPENAI_API_KEY
LLMChatter.Database.Password = YOUR_DATABASE_PASSWORD
```

Use the full key without quotes. The database password must match `.env`.
Then run `setup.ps1` normally to build and start the stack. Runtime configs are
ignored by Git and preserved when setup runs again; `config/` contains only
templates with blank credential fields. Never put your key in those templates.

For an existing installation, run `setup.ps1 -SkipBuild`, set the runtime key
and password, then run these commands from the `azerothcore-wotlk` directory
with the database already running:

```text
docker compose up -d --build --no-deps ac-llm-chatter-bridge
docker exec ac-llm-chatter-bridge python chatter_healthcheck.py --config /config/mod_llm_chatter.conf
```

The health check includes a small live API request. After changing the runtime
key or model, apply it with `docker compose restart ac-llm-chatter-bridge`.
Inspect output with `docker compose logs --tail=100 ac-llm-chatter-bridge`.
Test in-game delivery by sending a party message while grouped with bots.

Worldserver must be built with Playerbots and LLM Chatter for bot login and
dialogue to work; a stock upstream image does not contain this module collection.
Keep database backups when recreating the stack. The bridge does not replace them.

## Custom bot personalities

My personality catalog and seeding tool are under `tools\llm-chatter\bot-profiles`. The generator creates deterministic modern US-based personalities for every character on an `RNDBOT` account: 70% everyday players, 25% celebrity-inspired fictional personalities, and 5% wildcards.

Install the Python dependency once:

```powershell
py -m pip install -r .\tools\requirements.txt
```

Use the same database password configured in the private `.env` file. Preview five generated profiles without changing the database:

```powershell
py .\tools\llm-chatter\bot-profiles\seed_modern_bot_profiles.py --password "YOUR_DATABASE_PASSWORD" --sample 5
```

Apply the personalities:

```powershell
py .\tools\llm-chatter\bot-profiles\seed_modern_bot_profiles.py --password "YOUR_DATABASE_PASSWORD" --apply
```

Before applying changes, the script backs up the complete `llm_bot_identities` table under `tools\llm-chatter\bot-profiles\backups`. The tracked `catalog\personality-catalog.json` keeps personalities associated with character names, so they survive a Playerbots character or account rebuild. After intentionally rebuilding the bot pool, I can remove obsolete identity rows with:

```powershell
py .\tools\llm-chatter\bot-profiles\seed_modern_bot_profiles.py --password "YOUR_DATABASE_PASSWORD" --apply --prune-orphans
```

The database defaults to `127.0.0.1:3306`; `--host`, `--port`, and `--user` override that when needed.

## Client patch

This setup uses `client\patch-4.mpq`. With WoW completely closed, copy that file into the client's `Data` folder:

```text
C:\path\to\World of Warcraft 3.3.5a\Data\patch-4.mpq
```

Then edit `Data\enUS\realmlist.wtf` and set it to the server's LAN IP:

```text
set realmlist 192.168.1.100
```

Delete the client's `Cache` folder if old client data is still showing, then launch the game.
