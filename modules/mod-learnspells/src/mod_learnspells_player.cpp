#include "Player.h"
#include "WorldSession.h"

#include "mod_learnspells.h"

namespace
{
uint32 GetStarterGroundMount(uint8 race)
{
    switch (race)
    {
        case RACE_HUMAN: return 458;        // Brown Horse
        case RACE_ORC: return 580;          // Timber Wolf
        case RACE_DWARF: return 6777;       // Gray Ram
        case RACE_NIGHTELF: return 8394;    // Striped Frostsaber
        case RACE_UNDEAD_PLAYER: return 17462; // Red Skeletal Horse
        case RACE_TAUREN: return 18989;     // Gray Kodo
        case RACE_GNOME: return 10873;      // Red Mechanostrider
        case RACE_TROLL: return 8395;       // Emerald Raptor
        case RACE_BLOODELF: return 34795;   // Red Hawkstrider
        case RACE_DRAENEI: return 34406;    // Brown Elekk
        default: return 0;
    }
}
}

void LearnSpells::OnPlayerLevelChanged(Player* player, uint8 /*oldLevel*/)
{
    // Player::Create temporarily changes level before a new character has
    // reached its final starting state. Learning here gives level-one
    // characters endgame spell ranks that persist after creation.
    if (!player->IsInWorld())
        return;

    LearnAllSpells(player);
}

void LearnSpells::OnPlayerLogin(Player* player)
{
    LearnAllSpells(player);
}

void LearnSpells::OnPlayerLearnTalents(Player* player, uint32 /*talentId*/, uint32 /*talentRank*/, uint32 /*spellid*/)
{
    LearnAllSpells(player);
}

void LearnSpells::LearnAllSpells(Player* player)
{
    // Playerbots have their own spell/skill factory. Running both systems while
    // a bot character is being constructed teaches the temporary max-level
    // spellbook to the final low-level character.
    if (player->GetSession() && player->GetSession()->IsBot())
        return;

    if (player->IsGameMaster() && !EnableGamemasters)
        return;

    if (player->getClass() == CLASS_DEATH_KNIGHT && player->GetMapId() == 609)
        return;

    RemoveOverLevelSpells(player);
    LearnClassSpells(player);
    LearnTalentRanks(player);
    LearnProficiencies(player);
    LearnMounts(player);
    AddTotems(player);
}

void LearnSpells::RemoveOverLevelSpells(Player* player)
{
    for (auto const& spellList : SpellsList)
    {
        for (auto const& spell : spellList)
        {
            uint32 starterMount = GetStarterGroundMount(player->getRace());
            bool isEarlyMount = spell.spellId == SPELL_APPRENTICE_RIDING || spell.spellId == starterMount;
            bool isEarlyFlightSkill = spell.spellId == SPELL_EXPERT_RIDING || spell.spellId == SPELL_COLD_WEATHER_FLYING;
            bool isEarlyFlyingMount = player->GetLevel() >= 20 && (spell.spellId == 32235 || spell.spellId == 32243);

            if (isEarlyMount || isEarlyFlightSkill || isEarlyFlyingMount)
                continue;

            if (spell.requiredLevel <= player->GetLevel() || !player->HasSpell(spell.spellId))
                continue;

            if (spell.raceId != -1 && spell.raceId != player->getRace())
                continue;

            if (spell.classId != -1 && spell.classId != player->getClass())
                continue;

            if (spell.teamId != -1 && spell.teamId != player->GetTeamId())
                continue;

            player->removeSpell(spell.spellId, SPEC_MASK_ALL, false);
        }
    }
}

void LearnSpells::LearnClassSpells(Player* player)
{
    if (!EnableClassSpells && !EnableFromQuests)
        return;

    for (auto& spell : SpellsList[TYPE_CLASS])
    {
        if (spell.requiresQuest == 0 && !EnableClassSpells)
            continue;

        if (spell.requiresQuest == 1 && !EnableFromQuests)
            continue;

        if (spell.raceId == -1 || spell.raceId == player->getRace())
            if (spell.classId == player->getClass())
                if (spell.teamId == -1 || spell.teamId == player->GetTeamId())
                    if (player->GetLevel() >= spell.requiredLevel)
                        if (spell.requiredSpellId == -1 || player->HasSpell(spell.requiredSpellId))
                            if (!player->HasSpell(spell.spellId))
                                player->learnSpell(spell.spellId);
    }
}

void LearnSpells::LearnTalentRanks(Player* player)
{
    if (!EnableTalentRanks)
        return;

    for (auto& spell : SpellsList[TYPE_TALENTS])
        if (spell.classId == player->getClass())
            if (player->GetLevel() >= spell.requiredLevel)
                if (player->HasSpell(spell.requiredSpellId))
                    if (!player->HasSpell(spell.spellId))
                        player->learnSpell(spell.spellId);
}

void LearnSpells::LearnProficiencies(Player* player)
{
    if (!EnableProficiencies)
        return;

    for (auto& spell : SpellsList[TYPE_PROFICIENCIES])
        if (spell.classId == player->getClass())
            if (player->GetLevel() >= spell.requiredLevel)
                if (!player->HasSpell(spell.spellId))
                    player->learnSpell(spell.spellId);
}

void LearnSpells::LearnMounts(Player* player)
{
    if (!EnableApprenticeRiding && !EnableJourneymanRiding && !EnableExpertRiding && !EnableArtisanRiding && !EnableColdWeatherFlying)
        return;

    if (EnableApprenticeRiding)
    {
        player->learnSpell(SPELL_APPRENTICE_RIDING);
        if (uint32 starterMount = GetStarterGroundMount(player->getRace()))
            player->learnSpell(starterMount);
    }

    if (EnableExpertRiding && player->GetLevel() >= 20)
    {
        player->learnSpell(SPELL_EXPERT_RIDING);
        player->learnSpell(player->GetTeamId() == TEAM_ALLIANCE ? 32235 : 32243);
    }

    for (auto const& spell : SpellsList[TYPE_MOUNTS])
    {
        if (((spell.spellId == SPELL_APPRENTICE_RIDING || spell.requiredSpellId == SPELL_APPRENTICE_RIDING) && !EnableApprenticeRiding) ||
            ((spell.spellId == SPELL_JOURNEYMAN_RIDING || spell.requiredSpellId == SPELL_JOURNEYMAN_RIDING) && !EnableJourneymanRiding) ||
            ((spell.spellId == SPELL_EXPERT_RIDING || spell.requiredSpellId == SPELL_EXPERT_RIDING) && !EnableExpertRiding) ||
            ((spell.spellId == SPELL_ARTISAN_RIDING || spell.requiredSpellId == SPELL_ARTISAN_RIDING) && !EnableArtisanRiding) ||
            (spell.spellId == SPELL_COLD_WEATHER_FLYING && !EnableColdWeatherFlying) ||
            (spell.requiresQuest == 1 && !EnableFromQuests))
            continue;

        if (spell.raceId == -1 || spell.raceId == player->getRace())
            if (spell.classId == -1 || spell.classId == player->getClass())
                if (spell.teamId == -1 || spell.teamId == player->GetTeamId())
                    if (spell.requiredSpellId == -1 || player->HasSpell(spell.requiredSpellId))
                        if (player->GetLevel() >= spell.requiredLevel)
                            if (!player->HasSpell(spell.spellId))
                                player->learnSpell(spell.spellId);
    }
}

void LearnSpells::AddTotems(Player* player)
{
    if (player->getClass() != CLASS_SHAMAN)
        return;

    if (!EnableClassSpells || !EnableFromQuests)
        return;

    uint32 totems[4][3] =
    {
        {5175, 2, 4}, // Earth Totem, TotemCategory 2, Level 4
        {5176, 4, 10}, // Fire Totem, TotemCategory 4, Level 10
        {5177, 5, 20}, // Water Totem, TotemCategory 5, Level 20
        {5178, 3, 30} // Air Totem, TotemCategory 3, Level 30
    };

    for (int i = 0; i <= 3; i++)
        if (player->GetLevel() >= totems[i][2])
            if (!player->HasItemTotemCategory(totems[i][1]))
                player->AddItem(totems[i][0], 1);
}
