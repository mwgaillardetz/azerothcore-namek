#include "mod_learnspells.h"

void LearnSpells::OnLoadCustomDatabaseTable()
{
    QueryResult result = WorldDatabase.Query("SELECT `type_id`, `spell_id`, `team_id`, `race_id`, `class_id`, `required_level`, `required_spell_id`, `requires_quest` FROM `mod_learnspells`");

    if (!result)
        return;

    do
    {
        Field* fields = result->Fetch();
        uint8 typeId = fields[0].Get<uint8>();

        SpellList spell;
        spell.spellId = fields[1].Get<uint32>();
        spell.teamId = fields[2].Get<int8>();
        spell.raceId = fields[3].Get<int8>();
        spell.classId = fields[4].Get<int8>();
        spell.requiredLevel = fields[5].Get<uint8>();
        spell.requiredSpellId = fields[6].Get<int32>();
        spell.requiresQuest = fields[7].Get<uint8>();

        SpellsList[typeId].push_back(spell);
    } while (result->NextRow());
}
