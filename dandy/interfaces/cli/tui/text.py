import re
import textwrap
from pathlib import Path

from dandy.application.agent.session import session

_PATH_WORD_RE = re.compile(r'[A-Za-z0-9._~/-]+')
_FILE_EXTENSION_RE = re.compile(r'\.[A-Za-z0-9]*[A-Za-z][A-Za-z0-9]*$')


def _is_path_token(word: str) -> bool:
    if not _PATH_WORD_RE.fullmatch(word):
        return False

    if word in ('.', '..') or word.startswith('-'):
        return False

    return '/' in word or bool(_FILE_EXTENSION_RE.search(word))


def linkify_file_paths(description: str) -> str:
    """Wrap the file paths in a beat's description in clickable OSC 8 links.

    A whitespace-separated word is linked when it uses only path-safe
    characters, is not a dash flag or `.`/`..`, and either contains a `/` or
    ends in a dotted extension with a letter (so `src/foo.py` links while
    `lines`, `1-10`, `-q`, and `1.0.5` do not). Relative paths resolve against
    the session's project base path. The sequences are raw OSC 8 because
    blessed's `hyperlink` terminfo capability is unavailable.
    """

    def linkify(word_match: re.Match[str]) -> str:
        word = word_match.group(0)

        if not _is_path_token(word):
            return word

        path = Path(word).expanduser()

        if not path.is_absolute():
            path = session.project_base_path / path

        return f'\x1b]8;;{path.as_uri()}\x1b\\{word}\x1b]8;;\x1b\\'

    return re.sub(r'\S+', linkify, description)


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
                break_on_hyphens=False,
            )
            wrapped_content = wrapper.fill(line.strip())
            wrapped_lines.append(wrapped_content)

        wrapped_paragraphs.append('\n'.join(wrapped_lines))

    return '\n\n'.join(wrapped_paragraphs)
