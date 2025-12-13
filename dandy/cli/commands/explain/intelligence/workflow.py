from dandy import Prompt, recorder_to_html_file
from dandy.cli.commands.explain.intelligence.bots.code_explainer_bot import CodeExplainerBot
from dandy.cli.commands.explain.intelligence.decoders.files_decoder import FilesDecoder
from dandy.processor.decoder.exceptions import DecoderNoKeysRecoverableException


@recorder_to_html_file('explain_project_workflow')
def explain_project_workflow(user_input: str) -> str:
    file_paths = []

    try:
        file_paths = FilesDecoder().process(
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

    except DecoderNoKeysRecoverableException:
        return 'No files found.'

    code_explanation_intel = CodeExplainerBot().process(
        user_input=user_input,
        file_paths=file_paths,
    )

    return code_explanation_intel.text