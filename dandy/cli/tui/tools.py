import textwrap


def wrap_text_with_indentation(text, width=70):
    """
    Wrap text with preserved paragraph indentation.
    Each paragraph is wrapped independently, keeping its leading whitespace.
    """
    paragraphs = text.split('\n\n')  # Split on double newlines for paragraphs
    wrapped_paragraphs = []

    for para in paragraphs:
        # Split paragraph into lines to capture original indentation
        lines = para.split('\n')
        wrapped_lines = []

        for line in lines:
            if not line.strip():  # Empty line
                wrapped_lines.append('')
                continue

            # Detect leading whitespace (indentation)
            indent = len(line) - len(line.lstrip())
            leading_space = line[:indent]

            # Wrap the content part
            wrapper = textwrap.TextWrapper(
                width=width,
                initial_indent=leading_space,
                subsequent_indent=leading_space,
                break_long_words=False,
                break_on_hyphens=False
            )
            wrapped_content = wrapper.fill(line.strip())
            wrapped_lines.append(wrapped_content)

        # Join wrapped lines of this paragraph
        wrapped_paragraphs.append('\n'.join(wrapped_lines))

    # Join paragraphs with double newlines
    return '\n\n'.join(wrapped_paragraphs)