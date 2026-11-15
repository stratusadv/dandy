from dandy.domain.prompt.prompt import Prompt


def _paths_section() -> Prompt:
    return (
        Prompt()
        .sub_heading('Paths')
        .list(['All file and directory paths are relative to the project root.'])
    )
