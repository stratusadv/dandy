import itertools
import random
import re
import unittest

from dandy.interfaces.cli.thinking_phrases import (
    _ACTIONS,
    _AN_WORDS,
    OBJECT_FAMILIES,
    _INSTRUMENT_SLOTS,
    _INSTRUMENT_SLOT_BY_FAMILY,
    _article,
    thinking_phrase,
)


class TestThinkingPhrase(unittest.TestCase):
    def test_phrase_is_nonempty_single_line(self) -> None:
        for seed in range(50):
            random.seed(seed)
            phrase = thinking_phrase()

            self.assertTrue(phrase)
            self.assertNotIn('\n', phrase)
            self.assertNotIn('  ', phrase)

    def test_phrase_starts_with_a_known_action_verb(self) -> None:
        for seed in range(50):
            random.seed(seed)
            phrase = thinking_phrase()

            self.assertIn(phrase.split(' ', 1)[0], set(_ACTIONS))

    def test_phrase_mentions_an_object_from_a_family(self) -> None:
        phrases = {thinking_phrase() for _ in range(50)}
        all_objects = [name for names in OBJECT_FAMILIES.values() for name in names]

        for phrase in phrases:
            self.assertTrue(any(name in phrase for name in all_objects), phrase)

    def test_articles_match_the_object_sound(self) -> None:
        for words in OBJECT_FAMILIES.values():
            for word in words:
                first = word.lower().split(' ')[0].split('-')[0]
                expected = 'an' if first in _AN_WORDS else 'a'

                self.assertEqual(expected, _article(word))

    def test_every_action_has_a_valid_family(self) -> None:
        for families, slot_kind, slot_names in _ACTIONS.values():
            self.assertTrue(families)

            for family in families:
                self.assertIn(family, OBJECT_FAMILIES)

            if slot_kind == 'instrument':
                self.assertTrue(slot_names)

                family_slots = set(
                    itertools.chain.from_iterable(_INSTRUMENT_SLOT_BY_FAMILY[f] for f in families)
                )

                for slot_name in slot_names:
                    self.assertIn(slot_name, _INSTRUMENT_SLOTS)
                    self.assertIn(slot_name, family_slots)

    def test_folding_never_gets_an_instrument(self) -> None:
        random.seed(7)
        for _ in range(200):
            phrase = thinking_phrase()

            if phrase.startswith('Folding '):
                self.assertIn(' into ', phrase)

                before_fold = phrase.split(' into ', 1)[0]

                self.assertNotIn(' with ', before_fold)

    def test_generator_produces_many_combinations(self) -> None:
        random.seed(42)
        phrases = {thinking_phrase() for _ in range(3000)}

        self.assertGreater(len(phrases), 100)
        for phrase in phrases:
            self.assertRegex(phrase, r'^[A-Z]')

    def test_quirks_are_optional_and_grammatical(self) -> None:
        random.seed(11)
        phrases = [thinking_phrase() for _ in range(500)]
        with_quirk = [
            phrase
            for phrase in phrases
            if re.search(r'\b(with|via)\b|\b(Rhythmically|Thoughtfully|Precisely|Pinky)\b', phrase)
        ]

        self.assertTrue(with_quirk)
        self.assertLess(len(with_quirk), len(phrases))
