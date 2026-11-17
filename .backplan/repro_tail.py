"""Repro: task ends right after a question — the phrase line must not survive."""

import sys

from blessed import Terminal

from dandy.interfaces.cli.tui.story_progress import StoryProgress
from tests.interfaces.cli.intelligence.screen import MiniScreen, ScreenStdout

REAL = sys.__stdout__
term = Terminal(force_styling='default')
screen = MiniScreen(width=80, height=30)
out = ScreenStdout(screen)
sys.stdout = out

progress = StoryProgress(term)
settled_count = 0


def render_ticks(n):
    global settled_count
    for _ in range(n):
        beats = progress.beats
        if len(beats) > settled_count + 1:
            for beat in beats[settled_count:-1]:
                sys.stdout.write(progress.settled_frame(beat))
            settled_count = len(beats) - 1
        if settled_count == 0 or len(beats) > settled_count or progress.is_animating:
            sys.stdout.write(progress.tick_frame())
            sys.stdout.flush()


def ask(question):
    sys.stdout.write(progress.pause_at_fresh_line())
    sys.stdout.flush()
    print(f'{term.normal}\n{term.purple}Asking{term.normal}{term.normal}')
    print(f'{term.purple}↳{term.normal} {question}')
    print(term.purple('─' * term.width))
    sys.stdout.write(term.bold_blue('❯ '))
    sys.stdout.write('yes\n')
    print(term.purple('─' * term.width))
    progress.resume_animation()


sys.stdout.write(f'{term.normal}Executing request "test..."{term.normal}\n')
render_ticks(2)
ask('Last question?')
render_ticks(2)
# thread dies here with the placeholder still live

# the printer's end path:
for beat in progress.beats[settled_count:]:
    sys.stdout.write(progress.settled_frame(beat))

settle = progress.settle_animation()
if settle:
    sys.stdout.write(settle)
    sys.stdout.flush()

carry = progress.carry_prefix()
if carry:
    sys.stdout.write(carry)

sys.stdout.write(f'{term.normal}\n{term.bold_green}Request Completed in 1.0s{term.normal}\n')
sys.stdout.flush()

sys.stdout = REAL
for i, row in enumerate(screen.lines):
    line = ''.join(row).rstrip()
    marker = ' <<cursor' if i == screen.row else ''
    if line or marker:
        print(f'{i + 1:>2} |{line}|{marker}')
