#!/usr/bin/env python3
"""Seed deterministic modern-player profiles for managed random bots."""

import argparse
import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path

import mysql.connector


DEFAULT_BACKUP_DIR = Path(__file__).resolve().parent / "backups"
DEFAULT_CATALOG_PATH = (
    Path(__file__).resolve().parent / "catalog" / "personality-catalog.json"
)


EVERYDAY_JOBS = [
    "help-desk technician", "systems administrator", "DevOps engineer",
    "cloud operations engineer", "site reliability engineer",
    "software engineer", "network engineer", "security analyst",
    "database administrator", "QA automation engineer",
    "data-center technician", "IT support specialist",
    "electronic health-records analyst", "nurse", "paramedic",
    "respiratory therapist", "radiology technician", "pharmacist",
    "medical assistant", "physical therapist", "construction foreman",
    "electrician", "plumber", "welder", "heavy-equipment operator",
    "carpenter", "HVAC technician", "warehouse supervisor",
    "delivery driver", "high-school teacher", "community-college student",
    "graduate student", "accountant", "restaurant manager", "line cook",
    "bartender", "mechanic", "insurance adjuster", "postal worker",
]

CITIES = [
    "Atlanta, Georgia", "Austin, Texas", "Baltimore, Maryland",
    "Boise, Idaho", "Boston, Massachusetts", "Buffalo, New York",
    "Charlotte, North Carolina", "Chicago, Illinois", "Cincinnati, Ohio",
    "Cleveland, Ohio", "Columbus, Ohio", "Dallas, Texas", "Denver, Colorado",
    "Detroit, Michigan", "Houston, Texas", "Indianapolis, Indiana",
    "Jacksonville, Florida", "Kansas City, Missouri", "Las Vegas, Nevada",
    "Los Angeles, California", "Louisville, Kentucky", "Memphis, Tennessee",
    "Miami, Florida", "Milwaukee, Wisconsin", "Minneapolis, Minnesota",
    "Nashville, Tennessee", "New Orleans, Louisiana", "New York City",
    "Oakland, California", "Oklahoma City, Oklahoma", "Orlando, Florida",
    "Philadelphia, Pennsylvania", "Phoenix, Arizona", "Pittsburgh, Pennsylvania",
    "Portland, Oregon", "Providence, Rhode Island", "Raleigh, North Carolina",
    "Richmond, Virginia", "Sacramento, California", "Salt Lake City, Utah",
    "San Antonio, Texas", "San Diego, California", "San Jose, California",
    "Seattle, Washington", "St. Louis, Missouri", "Tampa, Florida",
]

HERITAGES = [
    "Appalachian", "Black American", "Cajun", "Chinese American",
    "Colombian American", "Cuban American", "Dominican American",
    "English American", "Filipino American", "Ghanaian American",
    "Greek American", "Guatemalan American", "Haitian American",
    "Indian American", "Irish American", "Italian American",
    "Jamaican American", "Japanese American", "Korean American",
    "Lebanese American", "Mexican American", "Nigerian American",
    "Pakistani American", "Polish American", "Puerto Rican American",
    "Salvadoran American", "Somali American", "Thai American",
    "Ukrainian American", "Vietnamese American", "Brazilian American",
]

FAMILY_ORIGINS = [
    "England", "China", "Mexico", "Brazil", "Jamaica", "Nigeria", "India",
    "Ireland", "Italy", "Poland", "Puerto Rico", "the Philippines", "Korea",
    "Vietnam", "Colombia", "Lebanon", "Ghana", "Ukraine", "Haiti", "Cuba",
]

HOBBIES = [
    "pickup basketball", "restoring old cars", "home-lab networking",
    "building mechanical keyboards", "karaoke", "camping", "fishing",
    "powerlifting", "distance running", "street photography", "cooking",
    "barbecue competitions", "tabletop games", "anime", "horror movies",
    "live punk shows", "metal concerts", "EDM festivals", "hip-hop shows",
    "indie concerts", "vinyl collecting", "woodworking", "gardening",
    "volunteering at an animal shelter", "coaching youth sports",
    "fantasy football", "skateboarding", "tattoo art", "open-mic comedy",
]

SOCIAL_LIVES = [
    "usually stay in with takeout and a small Discord group",
    "host crowded game nights in a cramped apartment",
    "go dancing most weekends but remain dependable at work Monday morning",
    "are regulars at local concerts and always protect friends in the pit",
    "like brewery trivia nights and argue cheerfully about music",
    "spend weekends at family cookouts and neighborhood block parties",
    "travel for festivals, sleep badly, and tell excellent road stories",
    "are rebuilding life after a rough party phase and value honest advice",
]

SUBSTANCE_CONTEXTS = [
    "do not use drugs and rarely drink",
    "drink socially, usually beer or a simple cocktail",
    "enjoy cannabis occasionally, usually as a low-dose gummy",
    "prefer a cannabis vape after chores are finished",
    "share a joint at concerts but avoid showing up impaired for work",
    "use a small pipe at home while listening to albums",
    "are sober now after years of heavy drinking and speak plainly about recovery",
    "have past experience with cocaine and pills, treat it as a costly mistake, and never glamorize it",
    "have survived opioid addiction and are serious about harm reduction and recovery",
    "party hard with alcohol on occasion but know when to call a ride",
]

CELEBRITIES = [
    "Jackie Chan", "Hulk Hogan", "Tupac Shakur", "Zach Galifianakis",
    "Robin Williams", "Amy Schumer", "Mark Hoppus", "Johnny Knoxville",
    "Dolly Parton", "Snoop Dogg", "Samuel L. Jackson", "Terry Crews",
    "Keanu Reeves", "Whoopi Goldberg", "Dave Grohl", "Missy Elliott",
    "Shaquille O'Neal", "Martha Stewart", "Conan O'Brien", "Jon Stewart",
    "Wanda Sykes", "Awkwafina", "Ken Jeong", "Lucy Liu", "Danny Trejo",
    "Pedro Pascal", "Salma Hayek", "John Leguizamo", "George Lopez",
    "Ali Wong", "Hasan Minhaj", "Mindy Kaling", "Donald Glover",
    "Queen Latifah", "Ice-T", "Busta Rhymes", "Eminem", "Post Malone",
    "Billie Eilish", "Lady Gaga", "Pink", "Miley Cyrus", "Willie Nelson",
    "Dave Chappelle", "Chris Rock", "Tiffany Haddish", "Steve-O",
    "Tony Hawk", "Mike Tyson", "Dwayne Johnson", "John Cena",
    "Serena Williams", "Simone Biles", "Dennis Rodman", "Guy Fieri",
    "Gordon Ramsay", "Alton Brown", "Neil deGrasse Tyson", "Bill Nye",
    "Weird Al Yankovic", "Jack Black", "Aubrey Plaza", "Nick Offerman",
    "Maya Rudolph", "Kristen Wiig", "Steve Carell", "Tina Fey",
    "Tracy Morgan", "Eric Andre", "Seth Rogen", "Jason Momoa",
    "Matthew McConaughey", "Jamie Foxx", "Viola Davis", "Octavia Spencer",
    "Morgan Freeman", "Danny DeVito", "Arnold Schwarzenegger",
    "Ozzy Osbourne", "Joan Jett", "Debbie Harry", "Questlove",
]

TRAITS = [
    "patient and practical", "dry-witted", "warm but blunt", "curious",
    "protective of new players", "methodical", "high-energy", "laid-back",
    "competitive but fair", "empathetic", "sarcastic", "quietly confident",
    "detail-oriented", "chaotic funny", "calm under pressure", "nostalgic",
    "helpful veteran", "skeptical but open-minded", "friendly introvert",
    "social organizer", "recovering perfectionist", "blue-collar direct",
]

TONES = [
    "casual, concise, and helpful", "friendly with dry humor",
    "patient and matter-of-fact", "energetic but never overwhelming",
    "warm, candid, and grounded", "blunt but supportive",
    "relaxed late-night gamer", "knowledgeable veteran without elitism",
]

WILDCARD_LIVES = [
    "a retired Coast Guard mechanic who now repairs bicycles for neighbors",
    "a touring sound engineer who has slept behind more venues than hotels",
    "a stay-at-home parent running a meticulous raid calendar between school pickups",
    "a food-truck owner testing recipes during dungeon queues",
    "a union organizer who believes every group works better with clear expectations",
    "a rural veterinarian accustomed to emergencies at impossible hours",
    "a tattoo artist who remembers customers by the stories behind their designs",
    "a public defender who decompresses with old raids after difficult cases",
    "a wildfire lookout who loves quiet zones and dependable radio etiquette",
    "a former touring drummer now teaching music at a community center",
]

ADVICE_SENTENCE = (
    "They know WoW as it existed in patch 3.3.5a and, when asked for gameplay "
    "help, answer directly with practical level ranges, zones, quest routes, "
    "dungeon entrances, roles, and mechanics; they admit uncertainty rather "
    "than inventing facts or mixing in later-expansion systems."
)


def stable_rank(guid, seed):
    value = f"{seed}:{guid}".encode("utf-8")
    return hashlib.sha256(value).digest()


def rng_for(guid, seed):
    digest = stable_rank(guid, seed)
    return random.Random(int.from_bytes(digest[:8], "big"))


def pick_distinct(rng, values, count=3):
    return rng.sample(values, count)


def everyday_profile(bot, rng):
    age = rng.randint(18, 59)
    city = rng.choice(CITIES)
    heritage = rng.choice(HERITAGES)
    origin = rng.choice(FAMILY_ORIGINS)
    job = rng.choice(EVERYDAY_JOBS)
    article = "an" if job[0].lower() in "aeiou" else "a"
    hobby = rng.choice(HOBBIES)
    social = rng.choice(SOCIAL_LIVES)
    substance = rng.choice(SUBSTANCE_CONTEXTS)
    relationship = rng.choice([
        "single and close with a few longtime friends",
        "married with a busy blended family",
        "divorced and rebuilding a comfortable routine",
        "living with a partner and two opinionated pets",
        "sharing rent with roommates while saving for a house",
        "helping care for an aging parent",
    ])
    backstory = (
        f"{bot['name']} is a {age}-year-old {heritage} from {city}, "
        f"raised in the United States in a family with roots in {origin}. "
        f"They work as {article} {job}, are {relationship}, and make time for {hobby}. "
        f"They {social}; they {substance}. Their humor and opinions come from "
        f"ordinary work, bills, family obligations, friendships, setbacks, and "
        f"trying to enjoy limited free time. {ADVICE_SENTENCE}"
    )
    return "modern_player", backstory


def celebrity_profile(bot, rng):
    celebrity = rng.choice(CELEBRITIES)
    city = rng.choice(CITIES)
    hobby = rng.choice(HOBBIES)
    substance = rng.choice(SUBSTANCE_CONTEXTS)
    backstory = (
        f"{bot['name']} uses a playful celebrity-inspired gaming persona modeled "
        f"on the publicly known style and energy of {celebrity}; this is fictional "
        f"roleplay, not a claim to be the real person or know private facts. They "
        f"imagine living in {city}, unwind with {hobby}, and {substance}. The voice "
        f"can echo recognizable comic, musical, athletic, or screen presence, but "
        f"should still sound like a cooperative everyday WoW player rather than a "
        f"constant impression or catchphrase machine. {ADVICE_SENTENCE}"
    )
    return "celebrity_inspired", backstory


def wildcard_profile(bot, rng):
    city = rng.choice(CITIES)
    life = rng.choice(WILDCARD_LIVES)
    hobby = rng.choice(HOBBIES)
    backstory = (
        f"{bot['name']} lives near {city} and is {life}. Their unusual schedule "
        f"left them with a broad mix of friends, hard-earned stories, and a talent "
        f"for explaining complicated things without talking down to anyone. They "
        f"also enjoy {hobby}. {ADVICE_SENTENCE}"
    )
    return "modern_wildcard", backstory


def build_profiles(bots, seed):
    ranked = sorted(bots, key=lambda bot: stable_rank(bot["guid"], seed))
    everyday_count = round(len(ranked) * 0.70)
    celebrity_count = round(len(ranked) * 0.25)
    profiles = []

    for index, bot in enumerate(ranked):
        rng = rng_for(bot["guid"], seed)
        if index < everyday_count:
            role, backstory = everyday_profile(bot, rng)
        elif index < everyday_count + celebrity_count:
            role, backstory = celebrity_profile(bot, rng)
        else:
            role, backstory = wildcard_profile(bot, rng)

        traits = pick_distinct(rng, TRAITS)
        profiles.append({
            **bot,
            "role": role,
            "traits": traits,
            "tone": rng.choice(TONES),
            "backstory": backstory,
        })
    return profiles


def portable_profile(row):
    """Normalize a DB/catalog/generated row without its wipe-prone GUID."""
    traits = row.get("traits")
    if traits is None:
        traits = [row.get("trait1"), row.get("trait2"), row.get("trait3")]
    traits = [str(value) for value in traits if value]
    return {
        "name": str(row.get("name") or row.get("bot_name") or ""),
        "role": str(row.get("role") or "modern_player"),
        "traits": traits[:3],
        "tone": str(row.get("tone") or "casual and grounded"),
        "backstory": str(row.get("backstory") or ""),
    }


def load_catalog(path):
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("profiles", [])
    return [portable_profile(row) for row in data if isinstance(row, dict)]


def catalog_by_name(*collections):
    result = {}
    for collection in collections:
        for row in collection:
            profile = portable_profile(row)
            if profile["name"]:
                result[profile["name"].casefold()] = profile
    return result


def restore_named_profiles(generated, saved_by_name):
    restored = 0
    profiles = []
    for profile in generated:
        saved = saved_by_name.get(profile["name"].casefold())
        if saved and len(saved["traits"]) == 3 and saved["backstory"]:
            profile = {
                **profile,
                "role": saved["role"],
                "traits": saved["traits"],
                "tone": saved["tone"],
                "backstory": saved["backstory"],
            }
            restored += 1
        profiles.append(profile)
    return profiles, restored


def write_catalog(path, saved_by_name, profiles):
    merged = dict(saved_by_name)
    for profile in profiles:
        portable = portable_profile(profile)
        merged[portable["name"].casefold()] = portable
    payload = {
        "format": "azerothcore-llm-bot-personalities-v1",
        "key": "case-insensitive character name",
        "note": "GUIDs are deliberately omitted so personalities survive bot wipes.",
        "profiles": sorted(merged.values(), key=lambda row: row["name"].casefold()),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3306)
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="password")
    parser.add_argument("--seed", default="coconut-modern-populace-v1")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--sample", type=int, default=0)
    parser.add_argument("--backup-dir", default=str(DEFAULT_BACKUP_DIR))
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG_PATH))
    parser.add_argument(
        "--prune-orphans", action="store_true",
        help="After backup/upsert, remove obsolete generated-profile GUID rows.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    connection = mysql.connector.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database="acore_characters",
    )
    cursor = connection.cursor(dictionary=True)
    query = (
        "SELECT c.guid, c.name FROM characters c "
        "JOIN acore_auth.account a ON a.id = c.account "
        "WHERE a.username REGEXP '^RNDBOT[0-9]+$' "
        "ORDER BY c.guid"
    )
    if args.limit:
        query += " LIMIT %s"
        cursor.execute(query, (args.limit,))
    else:
        cursor.execute(query)
    bots = cursor.fetchall()
    cursor.execute("SELECT * FROM llm_bot_identities ORDER BY bot_guid")
    existing = cursor.fetchall()
    catalog_path = Path(args.catalog)
    saved_by_name = catalog_by_name(load_catalog(catalog_path), existing)
    generated = build_profiles(bots, args.seed)
    profiles, restored = restore_named_profiles(generated, saved_by_name)

    counts = {}
    for profile in profiles:
        counts[profile["role"]] = counts.get(profile["role"], 0) + 1
    print(json.dumps({
        "bots": len(profiles),
        "restored_by_name": restored,
        "newly_generated": len(profiles) - restored,
        "roles": counts,
    }, indent=2))
    if args.sample:
        print(json.dumps(profiles[:args.sample], indent=2))

    if not args.apply:
        print("Dry run only; pass --apply to write profiles.")
        return

    backup_dir = Path(args.backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = backup_dir / f"llm_bot_identities_{stamp}.json"
    backup_path.write_text(
        json.dumps(existing, indent=2, default=str),
        encoding="utf-8",
    )

    upsert = (
        "INSERT INTO llm_bot_identities "
        "(bot_guid, bot_name, trait1, trait2, trait3, role, tone, backstory, "
        "identity_version) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1) "
        "ON DUPLICATE KEY UPDATE bot_name=VALUES(bot_name), "
        "trait1=VALUES(trait1), trait2=VALUES(trait2), "
        "trait3=VALUES(trait3), role=VALUES(role), tone=VALUES(tone), "
        "backstory=VALUES(backstory)"
    )
    values = [
        (
            profile["guid"], profile["name"], *profile["traits"],
            profile["role"], profile["tone"], profile["backstory"],
        )
        for profile in profiles
    ]
    cursor.executemany(upsert, values)
    affected = cursor.rowcount
    pruned = 0
    if args.prune_orphans:
        cursor.execute(
            "DELETE i FROM llm_bot_identities i "
            "WHERE i.role IN ('modern_player', 'celebrity_inspired', "
            "'modern_wildcard') AND NOT EXISTS ("
            "SELECT 1 FROM characters c JOIN acore_auth.account a "
            "ON a.id = c.account WHERE c.guid = i.bot_guid "
            "AND a.username REGEXP '^RNDBOT[0-9]+$')"
        )
        pruned = cursor.rowcount
    connection.commit()
    write_catalog(catalog_path, saved_by_name, profiles)
    print(f"Applied {affected} inserts/updates.")
    print(f"Pruned {pruned} orphaned generated-profile rows.")
    print(f"Backup: {backup_path.resolve()}")
    print(f"Portable catalog: {catalog_path.resolve()}")


if __name__ == "__main__":
    main()
