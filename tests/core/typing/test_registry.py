from unittest import TestCase

from dandy.core.typing.registry import resolve_type_from_registry, TYPE_REGISTRY

class TestRegistry(TestCase):
    def test_resolve_type_from_registry(self):
        for type_name, type_class in TYPE_REGISTRY.items():
            resolved_type = resolve_type_from_registry(type_name)
            self.assertEqual(resolved_type, type_class)
