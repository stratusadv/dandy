from dandy import config
from dandy.llm.handler import Handler


class OllamaHandler(Handler):
    @classmethod
    def setup(cls):
        cls.url = config.ollama.url
        cls.port = config.ollama.port
        cls.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        cls.path_parameters = [
            'api',
            'generate',
        ]
        cls.query_parameters = None
