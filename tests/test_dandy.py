import os
from unittest import TestCase

from dandy import config
from tests.factories import generate_current_work_order_schema_data, generate_existing_work_order_list_schema_data


class TestDandy(TestCase):
    def setUp(self):
        config.setup_ollama(
            url=os.getenv("OLLAMA_URL"),
            port=int(os.getenv("OLLAMA_PORT", 11434))
        )

        self.current_work_order = generate_current_work_order_schema_data()


    def test_workflow(self):
        pass
