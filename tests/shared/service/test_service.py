from unittest import TestCase

from dandy.shared.service.service import BaseService


class DummyService(BaseService):
    def reset(self) -> None:
        pass


class TestBaseService(TestCase):
    def test_init_stores_obj_and_recorder_event_id(self) -> None:
        obj = object()

        service = DummyService(obj=obj)

        self.assertIs(service.obj, obj)
        self.assertIsNotNone(service.recorder_event_id)
        self.assertEqual(service.obj_class, type(obj))

    def test_recorder_event_ids_are_unique_per_instance(self) -> None:
        first_service = DummyService(obj=object())
        second_service = DummyService(obj=object())

        self.assertNotEqual(first_service.recorder_event_id, second_service.recorder_event_id)

    def test_post_init_hook_runs_during_init(self) -> None:
        calls: list = []

        class HookService(BaseService):
            def __post_init__(self) -> None:
                calls.append(self.obj)

            def reset(self) -> None:
                pass

        obj = object()
        HookService(obj=obj)

        self.assertEqual(calls, [obj])

    def test_base_service_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            BaseService(obj=object())
