"""Compact, deterministic WoW 3.3.5a gameplay guidance retrieval."""

import re
from typing import Optional


_HELP_WORDS = re.compile(
    r"\b(where|what|which|how|help|guide|mechanic|strategy|strat|"
    r"quest|level|dungeon|raid|boss|entrance|range|do we|should i)\b",
    re.IGNORECASE,
)
_LEVEL = re.compile(r"\b(?:level|lvl|dinged?)?\s*(\d{1,2})\b", re.IGNORECASE)


ZONE_ROUTES = [
    (1, 9,
     "Alliance: Elwynn Forest, Dun Morogh, Teldrassil, Azuremyst Isle. "
     "Horde: Durotar, Mulgore, Tirisfal Glades, Eversong Woods."),
    (10, 19,
     "Alliance: Westfall, Loch Modan, Darkshore, Bloodmyst Isle. "
     "Horde: Northern Barrens, Silverpine Forest, Ghostlands. "
     "Both can use the shared cross-faction group system, but quest hubs remain faction-specific."),
    (20, 29,
     "Alliance: Redridge Mountains, Duskwood, Wetlands, Ashenvale. "
     "Horde: Southern Barrens, Stonetalon Mountains, Hillsbrad Foothills, Ashenvale. "
     "At 25, Duskwood/Wetlands are strong Alliance choices; Hillsbrad/Stonetalon are strong Horde choices."),
    (30, 39,
     "Stranglethorn Vale and Desolace work for both factions; also use Arathi Highlands, "
     "Alterac Mountains, and Dustwallow Marsh. Move between zones when quests turn orange/red."),
    (40, 49,
     "Tanaris, Feralas, and The Hinterlands are the main routes; add Searing Gorge around 43+ "
     "and Azshara for supplementary quest chains."),
    (50, 57,
     "Un'Goro Crater, Felwood, Burning Steppes, Western Plaguelands, then Eastern Plaguelands. "
     "Silithus and Winterspring are best toward the upper end."),
    (58, 61,
     "Enter Outland through the Dark Portal and quest in Hellfire Peninsula; move to "
     "Zangarmarsh around 60-61."),
    (62, 64,
     "Zangarmarsh, then Terokkar Forest. Nagrand becomes efficient around 64."),
    (65, 67,
     "Nagrand and Blade's Edge Mountains, with Netherstorm or Shadowmoon Valley beginning around 67."),
    (68, 71,
     "Start Northrend in Borean Tundra or Howling Fjord; both are designed for 68-72."),
    (72, 74,
     "Dragonblight is the primary route, with Grizzly Hills becoming comfortable around 73."),
    (75, 76,
     "Zul'Drak and the later Grizzly Hills chains; Sholazar Basin is excellent from 76."),
    (77, 80,
     "Sholazar Basin, then Storm Peaks and Icecrown. Buy Cold Weather Flying at 77 when eligible; "
     "Storm Peaks and Icecrown routing assumes flight."),
]


INSTANCES = {
    "naxxramas": "Naxxramas: level 80 introductory Wrath raid for 10 or 25 players, floating above eastern Dragonblight. Use the portal beneath it. Its four wings can be tackled in flexible order before Sapphiron and Kel'Thuzad; encounter execution matters more than a single linear route.",
    "ulduar": "Ulduar: level 80 raid for 10 or 25 players in northern Storm Peaks. Enter through the Antechamber complex after Flame Leviathan. Many bosses have optional hard modes triggered inside the encounter, so agree before pulling rather than activating one accidentally.",
    "obsidian sanctum": "Obsidian Sanctum: level 80 raid beneath Wyrmrest Temple in Dragonblight. It supports 10 or 25 players. Killing Sartharion with one to three drakes still alive activates progressively harder versions and better rewards.",
    "eye of eternity": "Eye of Eternity: level 80 10/25-player Malygos raid entered through the upper Nexus in Coldarra. One player needs the focusing key appropriate to the difficulty to start the encounter.",
    "trial of the crusader": "Trial of the Crusader: level 80 10/25-player raid at the Argent Coliseum in northeastern Icecrown. It is a five-encounter linear raid with no trash; Trial of the Grand Crusader is its heroic version.",
    "icecrown citadel": "Icecrown Citadel: level 80 10/25-player raid in southern Icecrown. Progress through the Lower Spire, then Plagueworks, Crimson Hall, and Frostwing Halls; defeating the wing end bosses unlocks the Lich King. Normal is commonly approached around item level 232+, with requirements depending heavily on group skill and server tuning.",
    "ruby sanctum": "Ruby Sanctum: level 80 10/25-player raid beneath Wyrmrest Temple. Clear the three lieutenants before Halion; heroic difficulty expects Icecrown-level gear and precise realm balancing.",
    "deadmines": "The Deadmines: recommended roughly 17-23. Entrance is in Moonbrook, Westfall. Clear through the mine and ship; interrupt caster mobs and avoid overpulling the tightly packed foundry/ship areas.",
    "wailing caverns": "Wailing Caverns: recommended roughly 17-24. Entrance is in the oasis southwest of the Crossroads in the Barrens; enter the skull-shaped cave, then follow the inner cavern. The layout loops, so complete all four Druids of the Fang before the final escort/event.",
    "scarlet monastery": "Scarlet Monastery: Graveyard about 28-35, Library 32-38, Armory 35-40, Cathedral 38-45. Entrance is northeast of Undercity in Tirisfal Glades. Cathedral has dense linked packs; clear the room before pulling Mograine and Whitemane.",
    "zul'farrak": "Zul'Farrak: recommended roughly 44-54. Entrance is northwest Tanaris. Bring the Mallet of Zul'Farrak if summoning Gahz'rilla; control the staircase waves and do not jump down before the group is ready.",
    "maraudon": "Maraudon: recommended roughly 46-55, with Princess runs usually 48+. Entrance is in the Valley of Spears, Desolace. Purple and orange wings converge; the Scepter of Celebras provides the inner portal shortcut after its quest chain.",
    "blackrock depths": "Blackrock Depths: roughly 50-60 and extremely large. Entrance is inside Blackrock Mountain, reached by the central chain structure and quarry. Decide on a route—prison, arena, bar, city, or emperor—before starting.",
    "stratholme": "Stratholme: roughly 55-60 for a comfortable full run, although entry is possible earlier. It is in northern Eastern Plaguelands. Main Gate leads toward the Scarlet side; Service Entrance requires the Key to the City and is used for undead/Baron runs. For the timed Baron rescue, kill the three ziggurat bosses and clear their crystals before the slaughterhouse.",
    "hellfire ramparts": "Hellfire Ramparts: roughly 58-63. Entrance is on the Hellfire Citadel ramparts in central Hellfire Peninsula. Watch patrols and keep Vazruden's dragon faced away from the party.",
    "the nexus": "The Nexus: roughly 69-73. Entrance is at the bottom of the Nexus structure in Coldarra, Borean Tundra. On Keristrasza, keep moving/jumping to clear Intense Cold stacks and move away with Crystallize.",
    "utgarde keep": "Utgarde Keep: roughly 68-72. Entrance is in central Howling Fjord. Spread for Keleseth's frost tombs and kill the tomb quickly; avoid Ingvar's frontal attacks and thrown axe path.",
    "azjol-nerub": "Azjol-Nerub: roughly 72-75. Entrance is in the Pit of Narjun, Dragonblight. On Anub'arak, handle add waves during burrow phases and keep moving away from Pursuing Spikes.",
    "ahn'kahet": "Ahn'kahet: The Old Kingdom is roughly 73-76, beside Azjol-Nerub in the Pit of Narjun. Interrupt Shadow Blast, kill Jedoga's volunteer before it reaches her, and on Herald Volazj defeat each player's insanity copies.",
    "drak'tharon keep": "Drak'Tharon Keep: roughly 74-77, on the Grizzly Hills/Zul'Drak border. On Novos, kill handlers to drop the barrier; on Tharon'ja, use the temporary skeleton abilities during Decay Flesh.",
    "violet hold": "Violet Hold: roughly 75-77, inside Dalaran. It is an eighteen-wave defense; keep the door sealed, use defense crystals for emergencies, and react to whichever two random bosses spawn.",
    "gundrak": "Gundrak: roughly 76-79, northeastern Zul'Drak. Activate the altars after bosses to open the final area; avoid Slad'ran's snake wraps and turn Gal'darah away during dangerous frontal attacks.",
    "halls of stone": "Halls of Stone: roughly 77-80, western Storm Peaks. During Tribunal of Ages protect Brann through the timed waves; on Sjonnir control the accumulating adds while maintaining boss damage.",
    "halls of lightning": "Halls of Lightning: roughly 78-80, northern Storm Peaks. Hide behind Bjarngrim's platform corners for Loken's Lightning Nova if needed, while staying close enough to limit Arc Lightning's distance-scaled damage.",
    "utgarde pinnacle": "Utgarde Pinnacle: roughly 78-80, upper Utgarde Keep. Harpoon Grauf during Skadi's gauntlet, then avoid whirlwind; on Ymiron stop attacking during Bane to avoid reflected shadow damage.",
    "oculus": "The Oculus: roughly 78-80, above the Nexus. Choose drakes after Drakos, use their role-specific abilities, and on Ley-Guardian Eregos coordinate time stops/evasion and kill planar anomalies during phase shifts.",
    "culling of stratholme": "The Culling of Stratholme: roughly 78-80, entered through Caverns of Time in Tanaris. Follow Arthas through staged waves; for the timed heroic run reach and defeat the Infinite Corruptor before the timer expires.",
    "trial of the champion": "Trial of the Champion: level 80, at the Argent Tournament in northeastern Icecrown. Equip a lance and use mounted shield-break/charge correctly, then fight champions on foot; move out of Eadric's Hammer target line or face away for Radiance.",
    "forge of souls": "Forge of Souls: level 80, inside Icecrown Citadel's upper entrance hub. On Bronjahm, keep corrupted souls from reaching him; on Devourer of Souls stop attacking during Mirrored Soul and avoid Wailing Souls by moving behind the rotating beam.",
    "pit of saron": "Pit of Saron: level 80, reached from Forge of Souls or the Frozen Halls entrance. Use saronite rocks to break Garfrost's Permafrost stacks; on Ick move from poison nova/explosives; during Tyrannus, avoid Rimefang's ice and stop attacking marked allies.",
    "halls of reflection": "Halls of Reflection: level 80, after Pit of Saron. Fight the opening waves from an alcove with line-of-sight control; dispel/interrupt aggressively. During the escape, stay with Jaina or Sylvanas and kill each wave before the Lich King reaches the group.",
}


BOSSES = {
    "patchwerk": "Patchwerk (Naxxramas): a healing and threat check. Keep the main tank highest on threat; Hateful Strike hits a nearby high-health, high-threat off-tank. Melee should not exceed tanks on threat. There is no positioning-heavy phase—beat the enrage timer.",
    "heigan": "Heigan the Unclean (Naxxramas): phase one has the boss tanked on the platform while ranged/healers avoid Spell Disruption; phase two is the floor 'dance.' Move through the four eruption sections in order, then reverse, without outrunning the safe section.",
    "loatheb": "Loatheb (Naxxramas): Necrotic Aura allows healing only during short windows. Healers pre-cast and land heals inside each window; DPS collect the Spore buff without killing spores before players are in range, and the raid uses consumables/defensives between windows.",
    "thaddius": "Thaddius (Naxxramas): kill Feugen and Stalagg together, make the platform jump, then obey polarity. Stack with the same charge and stay away from the opposite charge; swap sides immediately when Polarity Shift changes you.",
    "kel'thuzad": "Kel'Thuzad (Naxxramas): spread to reduce Frost Blast/Detonate Mana overlap, interrupt Frostbolt, move from Shadow Fissures, and crowd-control the phase-three guardians while finishing the boss. Frost Blast targets need immediate healing.",
    "sartharion": "Sartharion (Obsidian Sanctum): avoid flame walls and lava waves, move from void zones, and kill fire elementals away from lava. Leaving drakes alive increases difficulty; handle each drake's portal/add mechanic and avoid killing Sartharion before planned drake objectives.",
    "malygos": "Malygos (Eye of Eternity): keep sparks away from Malygos and kill them where DPS can stack their damage zones; hide in anti-magic bubbles during the platform phase. In the drake phase, maintain damage-over-time stacks, heal with combo points, and move as a group from Static Field.",
    "flame leviathan": "Flame Leviathan (Ulduar): use siege vehicles, demolishers, and choppers. Kite the boss, interrupt speed with towers/tar as applicable, launch passengers to destroy turrets and trigger Systems Shutdown, then unload pyrite damage during the vulnerability.",
    "ignis": "Ignis the Furnace Master (Ulduar): tank him facing away and place Scorch predictably. Drag Iron Constructs through Scorch until molten, then into water to make them brittle and shatter them; free players from Slag Pot with focused healing.",
    "xt-002": "XT-002 Deconstructor (Ulduar): spread for Light Bomb and Gravity Bomb and move them away from the raid. At heart phases, damage the exposed heart while controlling adds; killing the heart activates hard mode.",
    "kologarn": "Kologarn (Ulduar): tanks swap for stacking armor debuff. Ranged spread and run eye beams away; kill the right arm to free Stone Grip victims, then control rubble adds. Do not stand where the destroyed arm falls.",
    "auriaya": "Auriaya (Ulduar): line-of-sight pull her sentries to avoid a lethal pounce. Stack to split Sonic Screech, interrupt Sentinel Blast, quickly kill the Feral Defender while respecting its repeated lives, and move away from its void zone.",
    "hodir": "Hodir (Ulduar): free helpful NPCs, keep moving to clear Biting Cold, use Toasty Fires and Storm Power, and stand on fresh snowdrifts to survive Flash Freeze. Break frozen players/NPCs immediately afterward.",
    "thorim": "Thorim (Ulduar): split the raid between arena add control and the gauntlet team. The gauntlet reaches Thorim before the timer; afterward tanks swap for Unbalancing Strike and everyone avoids lightning lines while spreading Chain Lightning.",
    "freya": "Freya (Ulduar): defeat add waves correctly—kill the three elemental adds together, burst Detonating Lashers carefully, and interrupt/heal through the Ancient Conservator. Kill healing trees and avoid ground effects; hard mode leaves elders alive.",
    "mimiron": "Mimiron (Ulduar): phase one avoid mines and Shock Blast; phase two spread and dodge Laser Barrage; phase three tank the aerial unit with ranged threat and use magnetic cores; phase four destroy all three sections within about ten seconds of each other.",
    "general vezax": "General Vezax (Ulduar): normal mana regeneration is disabled. Casters use Saronite Vapor pools carefully for mana at a health cost; interrupt Searing Flames, move from Shadow Crash, and keep ranged spread. Hard mode avoids destroying vapors until the Animus forms.",
    "yogg-saron": "Yogg-Saron (Ulduar): phase one kill guardians near Sara without standing in clouds. Phase two enter portals, kill illusions, and exit before Induce Madness while outside players control tentacles. Phase three face away from Lunatic Gaze and kill immortal guardians as their health permits.",
    "algalon": "Algalon (Ulduar): tanks swap for Phase Punch before being phased, collapse stars carefully to control raid damage and black holes, move from Cosmic Smash, and use black holes to escape Big Bang unless protected by the intended immunity mechanic.",
    "northrend beasts": "Northrend Beasts (Trial of the Crusader): on Gormok swap tanks for Impale and kill Snobolds; on the jormungars manage poison/fire positioning and kill them close together; on Icehowl spread after Massive Crash and dodge his charge to earn the damage window.",
    "lord jaraxxus": "Lord Jaraxxus (Trial of the Crusader): interrupt Fel Fireball, dispel Nether Power, move Legion Flame out, and prioritize Mistress of Pain and Infernal adds from portals/volcanoes. Heal Incinerate Flesh fully before it expires.",
    "faction champions": "Faction Champions (Trial of the Crusader): this behaves like PvP. Coordinate crowd control and interrupts, purge buffs, apply mortal-strike effects, protect focused allies, and kill vulnerable healers or priority targets; conventional tank threat does not control them reliably.",
    "twin val'kyr": "Twin Val'kyr (Trial of the Crusader): take light or dark essence, attack the opposite-colored twin, absorb matching orbs, and avoid opposite orbs. Swap/coordinate essence for the shield and interrupt the heal after breaking the shield.",
    "anub'arak": "Anub'arak (Trial of the Crusader): manage burrowers and interrupt Shadow Strike on heroic; during burrow, kite spikes through frost patches. In phase three keep the raid deliberately low but stable because Leeching Swarm heals him based on current health; heal Penetrating Cold targets strongly.",
    "marrowgar": "Lord Marrowgar (Icecrown Citadel): tanks stack to split Saber Lash, ranged spread, kill Bone Spikes immediately, and move from Coldflame. During Bone Storm keep moving away while still freeing spiked players.",
    "deathwhisper": "Lady Deathwhisper (Icecrown Citadel): control and interrupt adds while damaging the mana shield; respect empowered/reanimated add immunities. In phase two tanks swap for Touch of Insignificance, interrupt Frostbolt, spread from ghosts, and continue killing remaining adds.",
    "gunship": "Gunship Battle (Icecrown Citadel): cannon players build heat without overheating and fire at the enemy ship; a strike team rockets across to kill the enemy mage freezing cannons, then returns before the stacking enemy commander becomes dangerous.",
    "saurfang": "Deathbringer Saurfang (Icecrown Citadel): ranged spread so Blood Beasts do not splash and kill/kite them without being hit. Tanks swap on Rune of Blood. Minimize Blood Power generation and heal Mark of the Fallen Champion targets through the finish.",
    "festergut": "Festergut (Icecrown Citadel): tanks swap around nine Gastric Bloat stacks. Ranged spread until spores spawn, then stack under assigned spores to gain three Inoculated stacks before Pungent Blight; collapse for healing during high inhale stacks as assigned.",
    "rotface": "Rotface (Icecrown Citadel): move Slime Spray away from the raid. Infected players run to the off-tank and let small oozes merge into the kited big ooze; after five merges, spread from the explosion projectiles.",
    "professor putricide": "Professor Putricide (Icecrown Citadel): the abomination drinks slime and slows oozes. Stack for green ooze impact, kite orange gas clouds, and avoid puddles/bombs. Push transitions cleanly; in phase three tanks rotate Mutated Plague and finish before room damage overwhelms healers.",
    "blood princes": "Blood Prince Council (Icecrown Citadel): attack only the empowered prince. Keep Kinetic Bombs airborne, spread for empowered shock vortex, move from flame orbs while letting them lose power, and have a ranged tank maintain shadow orbs for Keleseth's empowered lance.",
    "blood-queen": "Blood-Queen Lana'thel (Icecrown Citadel): bitten players gain strong damage and must bite an unbitten assigned player before Frenzied Bloodthirst expires. Link partners meet for Pact, flames go to room edges, and the raid spreads before the air phase.",
    "valithria": "Valithria Dreamwalker (Icecrown Citadel): the encounter ends by healing Valithria to full. Portal healers collect and maintain Emerald Vigor stacks, while the raid controls adds—especially suppressors, blazing skeletons, and dangerous interrupts—without letting the room collapse.",
    "sindragosa": "Sindragosa (Icecrown Citadel): manage stacking melee/caster debuffs, move Blistering Cold correctly, and place ice tombs without trapping the raid. In phase three alternate behind tombs to clear Mystic Buffet while keeping tomb targets alive but freeing them promptly.",
    "lich king": "The Lich King (Icecrown Citadel): phase one manage Necrotic Plague on adds and Shambling Horrors; transitions kill Raging Spirits. Phase two control Val'kyr and Defile with disciplined positioning. Phase three enter/handle Frostmourne, kill Vile Spirits, and never stand near the platform edge during transition mechanics.",
    "halion": "Halion (Ruby Sanctum): in the physical realm drop combustion at the edge and avoid meteor/fire; in twilight drop consumption at the edge and rotate around the cutters. Phase three balance damage between realms to keep Corporeality near 50/50.",
}


ALIASES = {
    "icc": "icecrown citadel", "toc": "trial of the crusader",
    "totc": "trial of the crusader", "os": "obsidian sanctum",
    "eoe": "eye of eternity", "naxx": "naxxramas", "rs": "ruby sanctum",
    "cos": "culling of stratholme", "hos": "halls of stone",
    "hol": "halls of lightning", "up": "utgarde pinnacle",
    "uk": "utgarde keep", "an": "azjol-nerub", "old kingdom": "ahn'kahet",
    "fos": "forge of souls", "pos": "pit of saron", "hor": "halls of reflection",
    "princes": "blood princes", "lana'thel": "blood-queen",
    "putricide": "professor putricide", "lk": "lich king",
}


MAP_INSTANCE_NAMES = {
    533: "Naxxramas", 603: "Ulduar", 615: "Obsidian Sanctum",
    616: "Eye of Eternity", 631: "Icecrown Citadel",
    649: "Trial of the Crusader", 724: "Ruby Sanctum",
    329: "Stratholme", 595: "Culling of Stratholme",
}


def _normalized(text: str) -> str:
    return re.sub(r"[^a-z0-9']+", " ", text.lower()).strip()


def _find_named_entry(message: str, entries: dict) -> Optional[str]:
    normalized = _normalized(message)
    padded = f" {normalized} "
    candidates = sorted(entries, key=len, reverse=True)
    for name in candidates:
        if f" {_normalized(name)} " in padded:
            return entries[name]
    for alias, canonical in sorted(ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if re.search(rf"\b{re.escape(_normalized(alias))}\b", normalized):
            if canonical in entries:
                return entries[canonical]
    return None


def retrieve_gameplay_guidance(
    player_message: str,
    *,
    map_id: int = 0,
) -> str:
    """Return a small trusted reference block for a gameplay question."""
    if not player_message or not _HELP_WORDS.search(player_message):
        return ""

    boss = _find_named_entry(player_message, BOSSES)
    if boss:
        detail = boss
    else:
        instance = _find_named_entry(player_message, INSTANCES)
        if instance:
            detail = instance
        else:
            level_match = _LEVEL.search(player_message)
            detail = ""
            if level_match and re.search(
                r"\b(quest|zone|area|level|lvl|go|leveling)\b",
                player_message,
                re.IGNORECASE,
            ):
                level = int(level_match.group(1))
                for minimum, maximum, route in ZONE_ROUTES:
                    if minimum <= level <= maximum:
                        detail = f"Level {level} questing route: {route}"
                        break
            if not detail and map_id in MAP_INSTANCE_NAMES and re.search(
                r"\b(this|current|here|dungeon|raid|instance|boss)\b",
                player_message,
                re.IGNORECASE,
            ):
                detail = (
                    f"Current instance: {MAP_INSTANCE_NAMES[map_id]}. "
                    "The question does not identify a boss; ask for the boss name "
                    "instead of inventing encounter mechanics."
                )

    if not detail:
        return ""
    return (
        "<wotlk_gameplay_reference>\n"
        "Trusted local reference for WoW 3.3.5a; factual instructions here "
        "override model memory. Answer the player's actual question directly, "
        "keep useful numbers/mechanics, and do not mention this reference block.\n"
        f"{detail}\n"
        "</wotlk_gameplay_reference>"
    )
