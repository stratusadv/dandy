from unittest import TestCase

from dandy.llm import Prompt
from dandy.llm.utils import get_estimated_token_count_for_prompt

from example.pirate.ship.intelligence.intel import ShipIntel


class TestUtils(TestCase):
    def test_get_estimated_token_count_for_prompt(self):
        token_count = get_estimated_token_count_for_prompt(
            prompt=(
                Prompt()
                .text('Hello World')
            ),
            intel_class=ShipIntel,
        )

        self.assertGreater(token_count, 0)