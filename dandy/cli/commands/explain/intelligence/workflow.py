from dandy import Prompt
from dandy.cli.commands.explain.intelligence.decoders.files_decoder import FilesDecoder


def explain_project_workflow(user_input: str):
    file_paths = FilesDecoder().process(
        prompt=(
            Prompt()
            .text('I am looking for files that would be help me learn about the following.')
            .text(user_input)
        )
    )

    print(file_paths)