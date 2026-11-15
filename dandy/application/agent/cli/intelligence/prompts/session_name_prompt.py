from dandy.domain.prompt.prompt import Prompt


def session_name_prompt(request_text: str) -> Prompt:
    return (
        Prompt()
        .text(
            'Write a short title for this coding request: 8 to 10 words, title '
            'case, plain words only (no quotes, no trailing punctuation, no '
            'markdown, no code). The title becomes the session name.'
        )
        .text('The request is between the delimiter lines below.')
        .text('--- BEGIN REQUEST ---')
        .text(request_text)
        .text('--- END REQUEST ---')
        .sub_heading('Response Format')
        .list(
            [
                (
                    'Respond with raw JSON only. Do not wrap the JSON in markdown '
                    'code fences and do not add any other text around it.'
                )
            ]
        )
    )
