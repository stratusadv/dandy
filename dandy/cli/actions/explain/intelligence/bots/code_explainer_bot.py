from pathlib import Path
from typing import Sequence

from dandy import Bot, Prompt


class CodeExplainerBot(Bot):
    role = 'Code Explainer'
    task = 'Explain how the code in the provided files works in reflection to the users request.'
    guidelines = (
        Prompt()
        .list([
            'Explain code in the order that a developer would need to learn it.',
            'Then proceed to explain what would be most relevant to the user after the base explanation.',
            'Use the code provided to then show an example',
        ])
    )

    def process(self, user_input: Prompt | str, file_paths: Sequence[Path | str]):
        prompt = Prompt()
        prompt.heading('User Request')
        prompt.text(user_input)
        prompt.line_break()

        prompt.heading('Files')
        for file_path in file_paths:
            prompt.file(
                file_path,
                triple_backtick=True,
                triple_backtick_label=str(file_path)
            )
            prompt.line_break()

        return self.llm.prompt_to_intel(prompt=prompt)