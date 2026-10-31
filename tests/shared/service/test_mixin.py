from unittest import TestCase

from dandy.shared.service.exceptions import ServiceCriticalError
from dandy.shared.service.mixin import BaseServiceMixin


class DummyService:
    def __init__(self, obj) -> None:
        self.obj = obj


class OtherService:
    def __init__(self, obj) -> None:
        self.obj = obj


class BaseMixinUser(BaseServiceMixin):
    def reset(self) -> None:
        pass


class TestBaseServiceMixin(TestCase):
    def test_get_service_instance_builds_and_caches(self) -> None:
        user = BaseMixinUser()

        first_instance = user._get_service_instance(DummyService)
        second_instance = user._get_service_instance(DummyService)

        self.assertIs(first_instance, second_instance)
        self.assertIs(first_instance.obj, user)

    def test_get_service_instance_caches_per_service_class(self) -> None:
        user = BaseMixinUser()

        dummy_instance = user._get_service_instance(DummyService)
        other_instance = user._get_service_instance(OtherService)

        self.assertIsNot(dummy_instance, other_instance)
        self.assertIs(other_instance.obj, user)

    def test_required_attrs_raise_service_critical_error_when_none(self) -> None:
        with self.assertRaises(ServiceCriticalError) as context:

            class BadMixinUser(BaseServiceMixin):
                _required_attrs = ('llm_config',)
                llm_config = None

        self.assertIn('llm_config', str(context.exception))

    def test_required_attrs_pass_when_set(self) -> None:
        class GoodMixinUser(BaseServiceMixin):
            _required_attrs = ('llm_config',)
            llm_config = 'DEFAULT'

            def reset(self) -> None:
                pass

        self.assertEqual(GoodMixinUser().llm_config, 'DEFAULT')
