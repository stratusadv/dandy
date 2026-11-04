from dataclasses import dataclass


@dataclass
class StoryBeat:
    """One line of the running story a long task narrates while it works.

    Tool action beats carry a short `label` (the tool's `action_label`, or the
    title-cased tool name) plus the per-call `description` built from the
    validated arguments (for example, the exact file or command). Plain
    sentences are description-only beats, and `kind` marks their voice:
    'system' (the default) for generic notices; 'compaction' for the
    notice the agent emits when it trims its own history; 'narration' for a
    sentence the model itself wrote alongside its tool calls. Tool
    beats also carry the tool's `can_mutate_state` flag so a UI can tell
    state-changing actions apart from read-only ones; the CLI renders their
    labels in bold skyblue, or bold orange when the beat can mutate state.
    UIs may style the label and the description
    independently.
    """

    label: str = ''
    description: str = ''
    kind: str = 'system'
    can_mutate_state: bool = False
