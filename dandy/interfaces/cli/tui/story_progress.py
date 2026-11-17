import threading
from time import perf_counter

from blessed import Terminal

from dandy.interfaces.cli.thinking_phrases import thinking_phrase
from dandy.interfaces.cli.tui.text import linkify_file_paths
from dandy.domain.tool.beat import StoryBeat

EVALUATING_PHRASE_CHANGE_SECONDS = 3.0

# The beat that stands in for the live region while a task has not pushed a
# story beat yet, so the thinking-phrase animation starts the moment a request
# is submitted.
_PLACEHOLDER_BEAT = StoryBeat(description='')


class StoryProgress:
    """Thread-safe accumulator for the story beats of a running task.

    The worker thread pushes `StoryBeat`s (AI summary sentences, tool action
    labels with their per-call detail, or plain notices) with `update`; the
    rendering thread prints them as a running list: consecutive tool beats
    with the same label share one heading line (the label in bold skyblue, or
    bold orange when the beat can mutate state), printed once when the label
    appears and again whenever the label changes or a non-tool line (a
    thought or a notice) has printed in between, and each beat's description
    prints below it on its own line prefixed by a `↳` arrow colored like
    the label. Each heading, and each narration, is preceded by a blank
    line. File paths in a tool beat's description are emitted as clickable
    file:// links. Non-tool beats (narration in bold blue, compaction
    notices in bold purple, system notices plain) print with no prefix.
    The newest beat animates with a bold blue thinking-phrase line below
    it: a random phrase is drawn once and held for
    `EVALUATING_PHRASE_CHANGE_SECONDS`, and the region is redrawn in place
    every tick. Every line is flush left.
    The animating frame folds a multi-line description onto the single line
    above the phrase line; the settled frame prints the beat's text in full,
    clearing every line it overwrites so no tail of the longer animating
    frame survives. The leftover phrase line is not deleted but reused as
    the first line of the next region, so beats within a group settle with
    no blank line between them.
    A question prompt pauses the animation: `pause_at_fresh_line` settles
    the newest beat (or the placeholder region) and lands on the fresh line
    below it, and `resume_animation` re-arms the placeholder region after the
    answer is delivered so the thinking phrase keeps moving while the model
    works on the answer, until the next real beat settles it. When the task
    ends with no beat following a question, `settle_animation` clears the
    leftover placeholder region so no orphaned thinking-phrase line survives
    above the completion line.
    """

    def __init__(self, term: Terminal) -> None:
        self.term = term
        self._beats: list[StoryBeat] = []
        self._lock = threading.Lock()
        self._heading_beat: StoryBeat | None = None
        self._heading_emitted: set[int] = set()
        self._evaluating_phrase: str | None = None
        self._evaluating_phrase_since: float = 0.0
        self._live_frame: bool = False
        self._live_beat: StoryBeat | None = None
        self._live_lines: int = 0
        self._live_desc_index: int = 1
        self._carry_lines: int = 0
        self._pending_animation: bool = False
        # The beat count the placeholder region was armed for at
        # resume_animation time: the placeholder keeps animating until a beat
        # beyond this count arrives. None while the placeholder is not in a
        # resumed state (the request-start case).
        self._animation_base_beat_count: int | None = None

    def update(self, beat: StoryBeat) -> None:
        with self._lock:
            self._beats.append(beat)

    @property
    def beats(self) -> list[StoryBeat]:
        with self._lock:
            return list(self._beats)

    def _needs_heading(self, beat: StoryBeat) -> bool:
        if not beat.label:
            return False

        beats = self.beats

        for index, current in enumerate(beats):
            if current is beat:
                if index == 0:
                    return True

                earlier = beats[index - 1]

                return not earlier.label or earlier.label != beat.label

        return True

    def _label_style(self, beat: StoryBeat) -> str:
        if beat.is_dangerous:
            return self.term.bold_red

        if beat.can_affect_system:
            return self.term.bold_orange

        if beat.can_mutate_state:
            return self.term.bold_purple

        return self.term.bold_skyblue

    def _styled_label(self, beat: StoryBeat) -> str:
        return f'\n{self._label_style(beat)}{beat.label}{self.term.normal}'

    def _styled_description(self, beat: StoryBeat, description: str) -> str:
        if beat.label:
            return linkify_file_paths(description)

        if beat.kind == 'narration':
            return f'\n{self.term.bold_blue}{description}{self.term.normal}'

        if beat.kind == 'compaction':
            return f'\n{self.term.bold_purple}{description}{self.term.normal}'

        return description

    def _emit_heading(self, beat: StoryBeat) -> str:
        if not self._needs_heading(beat) or id(beat) in self._heading_emitted:
            return ''

        self._heading_beat = beat
        self._heading_emitted.add(id(beat))

        # A bare LF keeps the cursor's column, so the description line below
        # the heading gets an explicit CR back to column zero.
        return f'{self.term.normal}{self._styled_label(beat)}{self.term.clear_eol()}\n\r'

    def _rotating_evaluating_phrase(self) -> str:
        """The current thinking phrase, re-drawn at most every 3 seconds."""
        now = perf_counter()

        if (
            self._evaluating_phrase is None
            or now - self._evaluating_phrase_since >= EVALUATING_PHRASE_CHANGE_SECONDS
        ):
            self._evaluating_phrase = thinking_phrase()
            self._evaluating_phrase_since = now

        return self._evaluating_phrase

    def drop_live_frame(self) -> None:
        """Forget the live frame so the next write starts on a fresh line."""
        self._live_frame = False
        self._live_beat = None
        self._live_lines = 0
        self._live_desc_index = 1
        self._carry_lines = 0

    @property
    def is_animating(self) -> bool:
        """Whether the thinking-phrase region is (or is about to be) live."""
        return self._pending_animation or (
            self._live_frame and self._live_beat is _PLACEHOLDER_BEAT
        )

    def resume_animation(self) -> None:
        """Arm the placeholder region to animate again from the next fresh line.

        Called after a question has been answered on the prompt's line, so the
        thinking phrase keeps moving while the model works on the answer,
        until the next real beat settles the region. Beats already in the list
        are considered settled, so the base count records them.
        """
        with self._lock:
            self._animation_base_beat_count = len(self._beats)
        self._pending_animation = True

    def tick_frame(self) -> str:
        """One animation step: the frame the render loop should write now.

        While no story beat has arrived yet, the placeholder beat animates the
        region so the thinking phrase is moving from the moment the request is
        submitted. The first real beat settles the placeholder region (its
        empty description line and phrase line) so the beat starts a fresh
        region with correct layout, even when the beat carries a heading.
        """
        with self._lock:
            has_beats = bool(self._beats)

        if self._pending_animation:
            # The region restarts after an answered question: the placeholder
            # animates on the fresh line below the prompt, and the next real
            # beat settles it through the normal path.
            self._pending_animation = False

            return self.frame(_PLACEHOLDER_BEAT)

        if has_beats:
            base_count = self._animation_base_beat_count

            if (
                self._live_frame
                and self._live_beat is _PLACEHOLDER_BEAT
                and base_count is not None
                and len(self._beats) <= base_count
            ):
                # A resumed placeholder: no new beat has arrived yet, so the
                # phrase keeps animating instead of redrawing an old beat.
                return self.frame(_PLACEHOLDER_BEAT)

            settle = self._settle_placeholder_if_live()

            if settle:
                self._animation_base_beat_count = None

            beat = self.beats[-1]
        else:
            settle = ''
            beat = _PLACEHOLDER_BEAT

        return f'{settle}{self.frame(beat)}'

    def _settle_placeholder_if_live(self) -> str:
        if not self._live_frame or self._live_beat is not _PLACEHOLDER_BEAT:
            return ''

        return self.settled_frame(_PLACEHOLDER_BEAT)

    def _placeholder_pause_settle(self) -> str:
        """Settle the live placeholder region for a pause.

        The placeholder's live lines hold no description text of their own
        (only a blank line and the phrase), so the settle is a plain clear
        rather than `settled_frame` (which would draw the tool-beat arrow
        prefix onto the prompt's line). The cursor sits on the phrase line
        after the last tick, so it clears just that line and climbs to the
        region's blank first line — the same landing a settled beat's phrase
        line carries — leaving the prompt's own leading newline as the only
        blank line of separation. Clearing both lines instead left a second
        blank line in the scrollback between every consecutive question.
        """
        live_lines = self._live_lines
        self._live_frame = False
        self._live_beat = None
        self._live_lines = 0
        self._live_desc_index = 1

        clear_phrase = f'\r{self.term.clear_eol()}'
        if live_lines > 1:
            clear_phrase += f'\x1b[{live_lines - 1}A\r'

        return clear_phrase

    def _fresh_line_prefix(self) -> str:
        carry = self._carry_lines
        self._carry_lines = 0
        return f'\x1b[{carry}A\r' if carry else '\r'

    def settle_animation(self) -> str:
        """Clear the live placeholder region when the task ends.

        If the last thing the model did was answer a question (so the region
        holds the resumed placeholder and no final beat ever arrived to
        settle it), the phrase line would otherwise survive above the
        completion line; settle it like a pause does, clearing the phrase and
        landing on the region's blank line so the completion sentence's
        leading newline leaves a single blank line of separation.
        """
        if not (self._pending_animation or self._live_frame):
            return ''

        if self._live_beat is not _PLACEHOLDER_BEAT:
            self._live_frame = False
            self._live_beat = None
            self._live_lines = 0
            self._live_desc_index = 1

            return ''

        return self._placeholder_pause_settle()

    def pause_at_fresh_line(self) -> str:
        """Stop the animation and land on a fresh line at column zero.

        Settles the newest beat while it still animates, then moves the
        cursor onto the leftover phrase line; used before a question prompt
        that must not share a line with the animating frame.
        """
        if not self._live_frame:
            return self._fresh_line_prefix()

        if self._live_beat is _PLACEHOLDER_BEAT:
            return self._placeholder_pause_settle()

        with self._lock:
            beats = list(self._beats)

        last_beat = beats[-1] if beats else _PLACEHOLDER_BEAT

        return self.settled_frame(last_beat) + self._fresh_line_prefix()

    def carry_prefix(self) -> str:
        """The cursor move onto a leftover carry line, or '' when there is none."""
        if not self._carry_lines:
            return ''

        return self._fresh_line_prefix()

    def _clear_line_tails(self, text: str) -> str:
        """Clear to the end of every line of `text` except the last.

        A settled multi-line description overwrites the live region line by
        line; without a clear per line, a longer old line would leave its
        tail visible behind the shorter new line.
        """
        parts = text.split('\n')

        for index in range(len(parts) - 1):
            parts[index] = f'{parts[index]}{self.term.clear_eol()}'

        return '\n'.join(parts)

    def settled_frame(self, beat: StoryBeat) -> str:
        heading = self._emit_heading(beat)
        description = self._styled_description(beat, beat.description)

        if beat.label:
            line = f'{self._label_style(beat)}↳{self.term.normal} {description}'
        else:
            line = f'{self.term.normal}{description}'

        # A bare LF keeps the cursor's column, so every line of a multi-line
        # description gets an explicit CR back to column zero.
        line = line.replace('\n', '\n\r')
        content = f'{heading}{line}'

        if not self._live_frame:
            return f'{self._fresh_line_prefix()}{content}{self.term.clear_eol()}\n\r'

        live_lines = self._live_lines
        desc_index = self._live_desc_index
        self._live_frame = False
        self._live_lines = 0
        self._live_desc_index = 1

        if description.startswith('\n'):
            # A narration region starts with a blank line; settle from the
            # region start so the content's leading newline lands the text
            # on its own line, and clear the stale start line.
            move_up = f'\x1b[{live_lines - 1}A\r{self.term.clear_eol()}'
            leftover_lines = max(0, live_lines - (content.count('\n') + 1))
        else:
            move_up = f'\x1b[{live_lines - desc_index}A\r'
            leftover_lines = max(0, (live_lines - desc_index + 1) - (content.count('\n') + 1))

        self._carry_lines = leftover_lines
        clear_leftover = f'{self.term.clear_eol()}\n\r' * leftover_lines

        return (
            f'{move_up}{self._clear_line_tails(content)}{self.term.clear_eol()}\n\r{clear_leftover}'
        )

    def frame(self, beat: StoryBeat) -> str:
        phrase = self._rotating_evaluating_phrase()
        heading = ''

        if self._heading_beat is not beat:
            heading = self._emit_heading(beat)
            self._heading_beat = beat

        prefix = (
            f'{self._label_style(beat)}↳{self.term.normal} ' if beat.label else self.term.normal
        )
        plain_description = ' '.join(beat.description.split())
        max_beat_length = max(1, self.term.width - len(prefix) - 1)

        if len(plain_description) > max_beat_length:
            description_part = plain_description[: max_beat_length - 1]
        else:
            description_part = plain_description

        beat_text = self._styled_description(beat, description_part)
        beat_line = f'{prefix}{beat_text}'
        evaluating_line = f'{self.term.bold_grey}✦ {phrase}{self.term.normal}'

        if self._live_frame:
            # A narration region's own text begins with a leading newline,
            # so a redraw must return to the region's start line; every
            # other region is re-drawn from its description line.
            up_lines = (
                self._live_lines - 1
                if beat_text.startswith('\n')
                else self._live_lines - self._live_desc_index
            )
            line_prefix = f'\x1b[{up_lines}A\r'
        else:
            line_prefix = self._fresh_line_prefix()
            # Redraws keep the region's layout; only a fresh frame can add a
            # heading line or a leading blank line (narration) above the
            # description line. A carry line only moves where the region
            # starts, not how tall it is.
            self._live_desc_index = (
                1 + (1 if heading else 0) + (1 if beat_text.startswith('\n') else 0)
            )
            self._live_lines = self._live_desc_index + 1

        frame_str = (
            f'{line_prefix}{heading}{beat_line}{self.term.clear_eol()}\n\r'
            f'{evaluating_line}{self.term.clear_eol()}'
        )

        self._live_frame = True
        self._live_beat = beat

        return frame_str
