from pathlib import Path

from dandy import Bot


class MarkdownBot(Bot):
    def __init__(
        self,
        markdown_file_path: str | Path
    ):
        with open(markdown_file_path, 'r') as f:
            self.llm_system_override_prompt = f.read()

        super().__init__()
