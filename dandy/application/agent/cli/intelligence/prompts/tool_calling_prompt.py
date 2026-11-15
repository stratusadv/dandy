from dandy.domain.prompt.prompt import Prompt


def _tool_calling_section(never_paste_text: str) -> Prompt:
    return (
        Prompt()
        .sub_heading('Calling Tools')
        .list(
            [
                (
                    'To perform an action, call the provided tool by name with its '
                    'arguments as a JSON object.'
                ),
                never_paste_text,
            ]
        )
    )
