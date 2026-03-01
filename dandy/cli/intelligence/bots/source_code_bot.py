from pathlib import Path

from dandy import Bot, Prompt, recorder_to_html_file
from dandy.cli.intelligence.intel.source_code_intel import SourceCodeIntel


class SourceCodeBot(Bot):
    role = 'Senior Developer'
    task = 'Read the instructions and write the source code for the user.'
    guidelines = Prompt().list([
        'You\'re only creating one file so focus on completeness.',
        'The file name should not contain a path and should be post fixed with `_bot`.',
            ])
    intel_class = SourceCodeIntel

    @recorder_to_html_file('source_code_bot')
    def process(
            self,
            user_input: str,
            code_reference_prompt: Prompt,
    ) -> SourceCodeIntel:
        self.llm.messages.add_message(
            role='user',
            text=(
                Prompt()
                .text('Below is the code I want you to reference while writing the source code for my next request.')
                .prompt(code_reference_prompt)
                .to_str()
            )
        )

        self.llm.messages.add_message(
            role='system',
            text='I have read through the provided code and will use it as a reference.'
        )

        return self.llm.prompt_to_intel(
            prompt=user_input,
        )
