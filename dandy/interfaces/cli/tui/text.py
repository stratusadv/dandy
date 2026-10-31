import textwrap


def wrap_text_with_indentation(text: str, width: int = 70) -> str:
    paragraphs = text.split('\n\n')
    wrapped_paragraphs = []

    for para in paragraphs:
        lines = para.split('\n')
        wrapped_lines = []

        for line in lines:
            if not line.strip():
                wrapped_lines.append('')
                continue

            indent = len(line) - len(line.lstrip())
            leading_space = line[:indent]

            wrapper = textwrap.TextWrapper(
                width=width,
                initial_indent=leading_space,
                subsequent_indent=leading_space,
                break_long_words=False,
                break_on_hyphens=False
            )
            wrapped_content = wrapper.fill(line.strip())
            wrapped_lines.append(wrapped_content)

        wrapped_paragraphs.append('\n'.join(wrapped_lines))

    return '\n\n'.join(wrapped_paragraphs)