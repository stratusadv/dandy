from unittest import TestCase

from tests.factories import generate_current_work_order, generate_existing_work_order_list


class TestDandy(TestCase):
    def setUp(self):
        self.current_work_order = generate_current_work_order()
        self.existing_work_order_list = generate_existing_work_order_list()

    def test_workflow(self):
        pass
