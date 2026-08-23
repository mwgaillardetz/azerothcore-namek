import unittest
import re

from chatter_constants import (
    HUMAN_PROXIMITY_CHAT_TOPICS,
    PROXIMITY_CHAT_TOPICS,
)


class HumanTopicSeparationTests(unittest.TestCase):
    def test_human_pool_is_populated_and_separate(self):
        self.assertGreaterEqual(len(HUMAN_PROXIMITY_CHAT_TOPICS), 20)
        self.assertIsNot(HUMAN_PROXIMITY_CHAT_TOPICS, PROXIMITY_CHAT_TOPICS)

    def test_human_pool_excludes_known_roleplay_seeds(self):
        combined = " ".join(HUMAN_PROXIMITY_CHAT_TOPICS).lower()
        for phrase in (
            'crows', 'omen', 'tavern', 'king', 'queen', 'prophecy',
            'village', 'town hall', 'graveyard', 'dalaran',
        ):
            self.assertIsNone(
                re.search(rf'\b{re.escape(phrase)}\b', combined)
            )

    def test_human_pool_contains_real_life_and_gameplay_subjects(self):
        combined = " ".join(HUMAN_PROXIMITY_CHAT_TOPICS).lower()
        for phrase in ('work', 'college', 'partner', 'bills', 'dungeon'):
            self.assertIn(phrase, combined)


if __name__ == '__main__':
    unittest.main()
