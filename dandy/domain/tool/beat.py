from dataclasses import dataclass


@dataclass
class StoryBeat:
    """One line of the running story a long task narrates while it works.

    Tool action beats carry a short `label` (the tool's `action_label`, or the
    title-cased tool name) plus the per-call `description` built from the
    validated arguments (for example, the exact file or command). Plain
    sentences are description-only beats, and `kind` marks their voice:
    'system' (the default) for the opening thinking phrase, 'Planning', and
    compaction notices; 'narration' for a sentence the model itself wrote
    alongside its tool calls. `ascii_char` is the character UIs prefix the
    beat line with; tool beats carry the tool's `action_ascii_char`, and an
    empty value means the renderer falls back to its default bullet. UIs may
    style the label, the description, and the kind independently.
    """

    label: str = ''
    description: str = ''
    kind: str = 'system'
    ascii_char: str = ''
