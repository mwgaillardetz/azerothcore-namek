# Migration and module recovery

## September 2026 incident

The restored `ac-worldserver` container used the public image
`acore/ac-wotlk-worldserver:master` (image ID beginning `c560a5edb521`). Its
startup log identified upstream master revision `7e18ca5b8db1` and loaded only
`mod_ale.conf`. Playerbots, LLM Chatter, and the other custom modules were absent.
The database still contained 1,000 random-bot characters and 14 other characters.
Configuration files alone cannot enable modules absent from the executable.

The custom build previously reused the public upstream image tag. That made a
registry pull during a move or recreation a valid-looking replacement for the
local custom build. The observed image and module list confirm this replacement;
the exact migration command was not retained in the evidence inspected.

The original `DBImport.log` identifies upstream master importer revision
`7c398fa9c298` and records 112 applied updates through `2026_08_30_05.sql`, while
the local Playerbots core source was still at its August 14 revision. An isolated
rebuild of that older source restored the modules but exposed missing quest
and raid scripts referenced by the newer database. It was not deployed. The
recovery therefore uses Playerbots revision `413bea61a85e20d9caef7d66fc601a661fdddd9d`
(September 4), followed by its matching database updates. The runtime checker
also rejects database script references with no corresponding compiled code.

The container creation date was August 31, and its last start before recovery
was September 8. The Python chatter bridge was added September 9, after the
worldserver image replacement.

## Prevention

- Worldserver, authserver, and the database importer use `namek/*:local` images
  with `pull_policy: never`. Missing custom images must be built or transferred;
  Compose cannot substitute public upstream images for those services.
- `setup.ps1` builds these services explicitly and checks native command exit
  codes. A failed clone, build, or image check stops deployment.
- Fresh checkouts use `core-revision.txt`, the core revision used for this
  recovery, rather than whatever the upstream branch contains on migration day.
  Existing server checkouts are preserved, but setup refuses a mismatched
  revision. Aligning their core is a separate operation after preserving local
  changes, rather than silently building an older or newer executable.
- Before deployment, setup checks every saved module config against the built
  image. It then waits for a healthy worldserver and rejects missing database
  script references. `tools/verify-runtime.py` also checks every module config
  against the running server's startup log.
- The worldserver Docker health check verifies both critical module configs and
  the local game port, so module loss is visible as an unhealthy container.
- The worldserver image includes Playerbots database-update files. Core and
  general module database updates run through the custom database importer;
  Playerbots handles its own database at worldserver startup.
- The MultiBot fallback compatibility handler is enabled because this module
  collection does not include a separate `mod-multibot-bridge`. Disable the
  fallback if you later install that separate module.
- Runtime configs and credentials remain outside source control and are not
  overwritten by repeated setup runs.

## Checklist for another host

1. Back up and restore all four databases: `acore_auth`, `acore_characters`,
   `acore_world`, and `acore_playerbots`. Keep a private backup of `.env` and
   runtime configs as well. Preserve or restore client data.
2. Run `setup.ps1 -SkipBuild` on Windows to prepare the checkout, then restore
   private runtime configs. On Linux, prepare the same checkout/modules,
   Dockerfiles, Compose file, `.env`, and runtime directories.
   If Docker volumes were restored outside Compose, reference those exact names
   as external volumes in the local override. The recovered Linux installation
   does this for its database, client data, and existing runtime logs.
3. Build the custom images before starting services. From the server checkout:

   ```bash
   docker compose build ac-worldserver ac-authserver ac-db-import ac-llm-chatter-bridge
   ```

   Alternatively transfer the exact custom images with `docker image save` and
   `docker image load`. A Docker volume backup does not contain custom images.
4. From the Namek repository, verify the built worldserver before deploying:

   ```bash
   python tools/verify-runtime.py --image namek/worldserver:local
   ```

5. Start the stack from the server checkout with `docker compose up -d --no-build`.
   Do not skip a required database import after a code/module upgrade.
6. After worldserver finishes starting, run `python tools/verify-runtime.py`
   from the Namek repository. Also run the chatter health check documented in
   the README.
7. Log in, allow random bots to populate, add an account character through
   MultiBot, and send a party message. This installation deliberately disables
   random bots while no real player is online, so an empty offline server alone
   does not prove a fault.

If a check fails, inspect the startup logs before opening the server to players.
Keep the previous images and a pre-upgrade database backup until validation is
complete; an old binary may not be compatible with an upgraded schema.

## Recovery validation

The aligned worldserver and importer were tested against a separate restoration
of all four databases before the live containers were replaced. All 20 expected
module configs loaded, every database script reference resolved, the game port
opened, and all 500 random bots logged in. Live bot gating remains unchanged:
bots wait for a real player, with a 60-second population update interval.

The live module/script check and chatter API check are repeated after cutover.
Private database and configuration backups are retained outside this repository.
The unrelated pending new-character bag SQL in the old checkout was not applied
as part of this recovery.

The existing chatter topic-separation tests pass, and PowerShell parsing and
Compose validation pass. The core-wide C++ style check reports pre-existing
issues in the pinned upstream source; no unrelated core reformatting was done.
