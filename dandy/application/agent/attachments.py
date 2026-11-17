from __future__ import annotations

import contextlib
import re
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from dandy.shared.files import encode_file_to_base64
from dandy.shared.constants import DANDY_LOCAL_DIRECTORY_NAME
from dandy.domain.tokens.estimate import (
    get_estimated_token_count_for_image,
    get_estimated_token_count_for_string,
)

ATTACHMENT_KIND_IMAGE = 'image'
ATTACHMENT_KIND_AUDIO = 'audio'
ATTACHMENT_KIND_PROJECT_FILE = 'project_file'

_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac'}

# A path-like token: a run of non-whitespace, non-quote characters. Slashes
# stay inside the token (so "a/b.txt" is one token, not two).
_PATH_TOKEN_RE = re.compile(r'[^\s\'"<>|*?]+')


@dataclass(frozen=True)
class TurnAttachment:
    """One file attached to a turn, classified for how it reaches the model.

    `image` and `audio` attachments go to the LLM as native content parts;
    `project_file` attachments are copied under `<project>/.dandy/attachments/`
    and the agent is told to read `delivery_path` with its own tools.
    """

    source_path: Path
    kind: str
    delivery_path: Path | None = None


def _is_path_like(token: str) -> bool:
    if '://' in token:
        return False

    # A token with a dot (a file in the project root), a slash, a backslash,
    # a leading ~, or a leading / (an absolute path) is worth checking for
    # existence; bare prose words and punctuation are not.
    return any(character.isalnum() for character in token) and (
        '.' in token or '/' in token or '\\' in token or token.startswith('~')
    )


def detect_attachment_paths(text: str, base_path: Path) -> tuple[str, list[Path]]:
    """Pull existing file-path tokens out of the input text.

    Returns the text with the tokens removed (surrounding text preserved) and
    the resolved paths that exist on disk. Relative paths resolve against
    `base_path` (the project root) and `~` expands to the home directory.
    """
    if not text:
        return text, []

    found: list[Path] = []
    removed_tokens: set[str] = set()

    for match in _PATH_TOKEN_RE.finditer(text):
        token = match.group(0)

        if not _is_path_like(token) or token in removed_tokens:
            continue

        candidate = Path(token).expanduser()

        if not candidate.is_absolute():
            candidate = base_path / candidate

        if not candidate.is_file():
            continue

        removed_tokens.add(token)
        found.append(candidate)

    remaining = text

    for token in removed_tokens:
        remaining = remaining.replace(token, ' ')

    return ' '.join(remaining.split()), found


def _attachment_kind(file_path: Path) -> str:
    suffix = file_path.suffix.lower()

    if suffix in _IMAGE_EXTENSIONS:
        return ATTACHMENT_KIND_IMAGE
    if suffix in _AUDIO_EXTENSIONS:
        return ATTACHMENT_KIND_AUDIO

    return ATTACHMENT_KIND_PROJECT_FILE


def _delivery_name(file_path: Path) -> str:
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%S')
    return f'{stamp}__{file_path.name}'


def _unique_delivery_path(directory: Path, name: str) -> Path:
    delivery = directory / name
    counter = 2
    suffix = Path(name).suffix
    stem = Path(name).name[: -len(suffix)] if suffix else name

    while delivery.exists():
        delivery = directory / f'{stem}-{counter}{suffix}'
        counter += 1

    return delivery


def prepare_turn_attachments(
    paths: list[Path], base_path: Path
) -> tuple[list[TurnAttachment], list[str]]:
    """Classify the detected paths and copy project files into the project.

    Images and audio stay where they are (the connector base64-encodes them);
    every other file is copied into `<base>/.dandy/attachments/` so the agent
    can read it with its read_file tool. Failures become issue strings and
    never raise.
    """
    attachments: list[TurnAttachment] = []
    issues: list[str] = []

    for source_path in paths:
        try:
            kind = _attachment_kind(source_path)

            if kind == ATTACHMENT_KIND_PROJECT_FILE:
                directory = base_path / DANDY_LOCAL_DIRECTORY_NAME / 'attachments'
                directory.mkdir(parents=True, exist_ok=True)
                delivery_path = _unique_delivery_path(directory, _delivery_name(source_path))
                shutil.copyfile(source_path, delivery_path)
                attachments.append(
                    TurnAttachment(source_path=source_path, kind=kind, delivery_path=delivery_path)
                )
            else:
                attachments.append(TurnAttachment(source_path=source_path, kind=kind))
        except Exception as error:
            issues.append(f'Could not attach "{source_path.name}": {error}')

    return attachments, issues


def attachments_token_count(attachments: list[TurnAttachment]) -> int:
    """The calibrated token estimate the attachments add to a turn.

    Images are priced at the high-detail default (they are attached at the
    wire default `auto`, which the estimator treats as high); audio is priced
    on its base64 payload size.
    """
    token_count = 0

    for attachment in attachments:
        if attachment.kind == ATTACHMENT_KIND_IMAGE:
            token_count += get_estimated_token_count_for_image(detail='auto')
        elif attachment.kind == ATTACHMENT_KIND_AUDIO:
            with contextlib.suppress(Exception):
                token_count += get_estimated_token_count_for_string(
                    encode_file_to_base64(attachment.source_path)
                )

    return token_count
