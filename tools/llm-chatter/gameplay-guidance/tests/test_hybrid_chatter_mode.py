import unittest
from unittest.mock import patch

from chatter_shared import get_chatter_mode


class HybridChatterModeTests(unittest.TestCase):
    def test_fixed_modes_remain_fixed(self):
        self.assertEqual(
            get_chatter_mode({'LLMChatter.ChatterMode': 'normal'}),
            'normal',
        )
        self.assertEqual(
            get_chatter_mode({'LLMChatter.ChatterMode': 'roleplay'}),
            'roleplay',
        )

    @patch('chatter_shared.random.random', return_value=0.84)
    def test_hybrid_uses_human_mode_inside_threshold(self, _random):
        config = {
            'LLMChatter.ChatterMode': 'hybrid',
            'LLMChatter.HumanConversationChance': '85',
        }
        self.assertEqual(get_chatter_mode(config), 'normal')

    @patch('chatter_shared.random.random', return_value=0.85)
    def test_hybrid_uses_roleplay_at_threshold(self, _random):
        config = {
            'LLMChatter.ChatterMode': 'hybrid',
            'LLMChatter.HumanConversationChance': '85',
        }
        self.assertEqual(get_chatter_mode(config), 'roleplay')

    @patch('chatter_shared.random.random', return_value=0.50)
    def test_percentage_is_clamped(self, _random):
        self.assertEqual(get_chatter_mode({
            'LLMChatter.ChatterMode': 'hybrid',
            'LLMChatter.HumanConversationChance': '200',
        }), 'normal')
        self.assertEqual(get_chatter_mode({
            'LLMChatter.ChatterMode': 'hybrid',
            'LLMChatter.HumanConversationChance': '-1',
        }), 'roleplay')

    @patch('chatter_shared.random.random', return_value=0.84)
    def test_invalid_percentage_uses_85_default(self, _random):
        self.assertEqual(get_chatter_mode({
            'LLMChatter.ChatterMode': 'hybrid',
            'LLMChatter.HumanConversationChance': 'not-a-number',
        }), 'normal')


if __name__ == '__main__':
    unittest.main()
