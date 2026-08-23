import unittest

from chatter_gameplay_knowledge import retrieve_gameplay_guidance


class GameplayKnowledgeTests(unittest.TestCase):
    def test_level_25_route(self):
        result = retrieve_gameplay_guidance("where should I quest at level 25?")
        self.assertIn("Duskwood", result)
        self.assertIn("Hillsbrad", result)

    def test_named_dungeon(self):
        result = retrieve_gameplay_guidance("recommended range for Stratholme?")
        self.assertIn("55-60", result)
        self.assertIn("Service Entrance", result)

    def test_boss_alias(self):
        result = retrieve_gameplay_guidance("what is the strat for Putricide?")
        self.assertIn("abomination", result)
        self.assertIn("phase three", result)

    def test_current_instance_without_boss(self):
        result = retrieve_gameplay_guidance(
            "how do we do this boss?", map_id=631
        )
        self.assertIn("Icecrown Citadel", result)
        self.assertIn("ask for the boss name", result)

    def test_ordinary_chat_has_no_context(self):
        self.assertEqual(
            retrieve_gameplay_guidance("nice pull, that was clean"), ""
        )


if __name__ == "__main__":
    unittest.main()
