from dandy import config
from dandy.llm.handler import Handler


class OllamaHandler(Handler):
    address = config.ollama.address
    port = config.ollama.port
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
