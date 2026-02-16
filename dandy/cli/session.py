from pathlib import Path

from dandy import BaseIntel


class DandyCliSession(BaseIntel):
    project_base_path: Path | str


session = DandyCliSession()