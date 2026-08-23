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
