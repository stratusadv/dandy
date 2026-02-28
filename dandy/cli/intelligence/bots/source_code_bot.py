from pathlib import Path

from dandy import Bot
from dandy.cli.intelligence.intel.source_code_intel import SourceCodeIntel


class SourceCodeBot(Bot):
    intel_class = SourceCodeIntel

    def process(self, user_input: str) -> None:
        pass
