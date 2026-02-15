from time import time

from dandy import Prompt, recorder_to_html_file
from dandy.cli.actions.explain.intelligence.bots.code_explainer_bot import (
    CodeExplainerBot,
)
from dandy.cli.actions.explain.intelligence.decoders.files_decoder import (
    FilesDecoderBot,
)
from dandy.cli.tui.tui import Tui
from dandy.llm.decoder.exceptions import DecoderNoKeysRecoverableError


@recorder_to_html_file('explain_project_workflow')
def explain_project_workflow(user_input: str) -> str:
    start_time = Tui.print_start_task('Searching', 'project structure')

    try:
        file_paths = FilesDecoderBot().process(
            prompt=(
                Prompt()
                .sub_heading('User Request:')
                .text(user_input)
                .line_break()
                .sub_heading('Instructions:')
                .text('I am looking for files that would be help me with my request.')
                .text('Please give me the file paths for anything that would help with my full request.')
            )
        )

        Tui.print_end_task(start_time)

    except DecoderNoKeysRecoverableError:
        Tui.print_end_task(start_time, 'No Files Found')
        return 'No files found.'

    start_time = Tui.print_start_task('Generating', 'code explanation')

    code_explanation_intel = CodeExplainerBot().process(
        user_input=user_input,
        file_paths=file_paths,
    )

    Tui.print_end_task(start_time)

    return code_explanation_intel.text