import os
from unittest import TestCase

from dandy import config
from tests.factories import generate_current_work_order, generate_existing_work_order_list


class TestDandy(TestCase):
    def setUp(self):
        config.setup_ollama(
            url=os.getenv("OLLAMA_URL"),
            port=int(os.getenv("OLLAMA_PORT", 11434))
        )

        self.current_work_order = generate_current_work_order()
        self.existing_work_order_list = generate_existing_work_order_list()

    def test_workflow(self):
        pass
