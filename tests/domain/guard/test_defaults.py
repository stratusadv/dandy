from unittest import TestCase

from dandy.domain.guard.context_guard import ContextPressureGuard
from dandy.domain.guard.defaults import default_guards
from dandy.domain.guard.repeat_guard import RepeatGuard


class TestDefaultGuards(TestCase):
    def test_returns_the_shipped_guards(self) -> None:
        guards = default_guards()

        self.assertIsInstance(guards[0], RepeatGuard)
        self.assertIsInstance(guards[1], ContextPressureGuard)

    def test_returns_fresh_instances_each_call(self) -> None:
        first = default_guards()
        second = default_guards()

        self.assertIsNot(first[0], second[0])
        self.assertIsNot(first[1], second[1])
