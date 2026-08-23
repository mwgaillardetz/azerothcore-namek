# LLM Chatter gameplay guidance implementation

## Purpose

This package archives the local WoW 3.3.5a gameplay-guidance implementation
used by `mod-llm-chatter`. It makes bot answers deterministic enough for common
leveling, dungeon, raid, and boss questions while preserving each bot's voice.

It also archives the hybrid human/RP conversation implementation. With
`LLMChatter.ChatterMode = hybrid`, each exchange is resolved once as either
ordinary-player conversation or immersive roleplay. The live configuration
uses `LLMChatter.HumanConversationChance = 85`, so human conversation is the
default while approximately 15% of exchanges retain full race/class flavor.

The live module remains under the AzerothCore checkout. Files here are a
portable snapshot and rollback/deployment package; they are not loaded directly
by the running bridge.

## Architecture

`chatter_gameplay_knowledge.py` contains:

- A cheap gameplay-question intent check.
- Level extraction and faction-aware questing routes from 1 through 80.
- Dungeon and raid aliases, recommended ranges, entrances, and practical tips.
- Major Wrath raid-boss mechanics through Ruby Sanctum.
- Map-aware fallback behavior for questions such as "this boss."
- A compact `<wotlk_gameplay_reference>` prompt block whose facts override the
  language model's unaided memory.

Retrieval runs locally and does not make another API request. Ordinary
conversation receives no reference block, so it adds no prompt cost outside
gameplay-help questions.

## Integration points

The archived `module-files/` directory contains the complete versions of every
live Python file changed for this feature:

| File | Player-response path |
| --- | --- |
| `chatter_gameplay_knowledge.py` | Knowledge catalog and retriever |
| `chatter_general.py` | General channel |
| `chatter_proximity.py` | Nearby `/say`, single and multi-bot |
| `chatter_group_prompts.py` | Party and raid, single and multi-bot |
| `chatter_guild_player.py` | Guild player replies |
| `chatter_shared.py` | Hybrid-mode resolution and percentage clamping |
| `chatter_group.py` | Persistent backstory selection for party/raid replies |
| `chatter_group_handlers.py` | Carries backstories into multi-bot replies |
| `llm_chatter_bridge.py` | Reports configured hybrid mode and human percentage |

The integration files import `retrieve_gameplay_guidance()`, pass the player's
message and map ID when available, and insert a returned reference before the
answer instructions. Guild replies temporarily allow normal gameplay terms
when a reference is present.

No C++ rebuild is required for this implementation. The bridge loads these
Python files from its bind mount and only needs a restart after deployment.

## Human conversation and persistent personality

Human mode frames bots as real people playing WoW rather than fantasy races
performing continuously. Race, class, zone, and encounter information remains
available when relevant, but daily life, work, family, hobbies, humor, and
personal opinions can shape ordinary conversation.

General, proximity, and party/raid player replies now load persistent traits,
tone, and backstory from `llm_bot_identities` or `llm_group_bot_traits`.
Backstories are marked as private prompt context: the model should draw from
them subtly and never recite the biography. Nearby NPC speakers stay in-world
even when a hybrid roll chooses human mode; the human framing applies only when
the speakers are playerbots.

Normal-mode proximity chatter now uses a dedicated everyday-player topic pool.
This is separate from the original proximity pool, which includes omens, crows,
tavern rumors, royalty, village gossip, and other fantasy-world subjects.
Hybrid roleplay rolls and NPC conversations can still use that material, while
normal playerbots draw from work, school, family, IT operations, bills, food,
entertainment, relationships, hobbies, substances, and practical WoW talk. A
direct player message is never replaced by an ambient topic: the bot continues
the conversation the player actually started.

The hybrid percentage is intentionally independent of gameplay guidance. A bot
can give the same factual 3.3.5a answer in either a casual-player voice or an
occasional immersive RP voice.

`hybrid-personality.conf.example` records the non-secret configuration snippet.
The live config itself is deliberately not archived because it contains API and
database credentials.

## Current coverage and limitations

Coverage includes level 1-80 quest routes, commonly requested Classic/TBC/Wrath
dungeons, all major Wrath raids, and major encounter mechanics for Naxxramas,
Ulduar, Trial of the Crusader, Icecrown Citadel, and Ruby Sanctum.

Named bosses are resolved precisely. The existing group event includes map and
zone information but not the player's selected target. Therefore, "How do we
do this boss?" can identify the current raid but asks for the boss name instead
of guessing. Adding target name/entry to the C++ player-message event would
remove that limitation but would require rebuilding the module.

The catalog is curated rather than a full quest-objective database. Unknown
questions fall back to the model's general knowledge under an explicit
instruction to admit uncertainty.

## Validate and deploy

The sync utility defaults to a read-only hash comparison:

```powershell
& .\sync-gameplay-guidance.ps1
```

Deploy the archived snapshot to the configured AzerothCore checkout explicitly:

```powershell
& .\sync-gameplay-guidance.ps1 -Mode Install
docker restart ac-llm-chatter-bridge
```

The sync utility deploys Python files and tests only. Apply the values from
`hybrid-personality.conf.example` to the live module config separately; this
prevents the utility from overwriting credentials or unrelated server tuning.

Capture a newer live implementation back into this archive:

```powershell
& .\sync-gameplay-guidance.ps1 -Mode Capture
```

Override `-ProjectRoot` if the checkout moves. The path must resolve to an
AzerothCore source root containing `modules/mod-llm-chatter/tools`.

Run the focused tests from the live AzerothCore root:

```powershell
$env:PYTHONPATH = 'modules/mod-llm-chatter/tools'
py -m unittest modules/mod-llm-chatter/tools/tests/test_gameplay_knowledge.py -v
py -m unittest modules/mod-llm-chatter/tools/tests/test_hybrid_chatter_mode.py -v
py modules/mod-llm-chatter/tools/import_smoke_check.py
```

## Extending the catalog

Add canonical entries to `INSTANCES` or `BOSSES`, then add common abbreviations
to `ALIASES`. Prefer actionable facts: level range, entrance, positioning,
interrupts, dispels, add priorities, tank swaps, and wipe-causing mechanics.
Keep each entry short because it is inserted into a chat prompt.

Add a focused unit test for every new alias or routing rule. After editing the
live module, run `-Mode Capture` to refresh this repository's snapshot.

## Rollback

Before installing an older snapshot, preserve the current live files with
`-Mode Capture` in a separate branch or commit. Git can then restore either
version. Restarting only `ac-llm-chatter-bridge` reloads the Python files; the
worldserver and character database do not need to restart.
