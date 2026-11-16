# Paste large text, images, and files into the CLI input

- Developer: nathanj (nathanj)
- Status: Planning
- Date: 2026-11-16-11-26

## End State

Pasting multi-line text into the dandy CLI REPL lands in the input as one atomic
block (rendered as a compact `⤶ N lines · X KB` indicator, sent to the model
verbatim), and any image or file path in typed/pasted input is attached to the
turn — image/audio files go to the LLM as native vision/audio content, all other
files are copied under `<project>/.dandy/attachments/` and their saved paths are
handed to the agent to read with its own tools — with hermetic tests, docs, and a
green suite.

## Observable Concern

Terminals deliver the bracketed-paste markers (`ESC[200~` … `ESC[201~`) in bursts
that blessed may split across several `inkey()` calls, so the paste-start/end
sequence detection must buffer a few characters with a short timeout — and on
timeout fall back to treating the buffered bytes as ordinary keys — or the input
line will eat a stray Escape/bracket keystroke the user typed by hand.

## Current State

- `dandy/interfaces/cli/tui/tui.py`: `get_user_input` reads `term.inkey(timeout=None)`
  in a `cbreak` loop; every non-sequence key appends one character to `self._buffer`
  and `_render` rewrites the whole (possibly wrapped) line per keystroke. Enter on
  a non-empty buffer submits. There is no bracketed-paste handling anywhere
  (grep for `bracketed`/`2004` finds nothing), so a multi-line paste replays every
  newline as Enter → spamming submits / corrupts the input.
- `Agent.turn(message: Prompt | str | None)` (`dandy/application/agent/agent.py`):
  the message becomes a single text `user` message via `ToolService` →
  `LlmService.prompt_to_intel` → `LlmConnector._update_request_body_options`, which
  only knows how to add a text user message for `prompt` — media kwargs
  (`image_file_paths`, `audio_file_paths`, …) would be added as **separate**
  user messages.
- `LlmService.prompt_to_intel` / `LlmConnector.prompt_to_intel` already accept
  `image_urls/image_file_paths/image_base64_strings` and `audio_*` and
  `Message.add_message(role='user', text=..., image_file_paths=...)` builds a
  **single** user message with mixed content parts (`dandy/domain/message/message.py`).
- `ToolService.prompt_to_intel` (`dandy/application/tool/service.py`) forwards
  `**kwargs` to `self.obj.prompt_to_intel` on iteration 0 only, so new media kwargs
  would flow through the tool loop without touching it.
- `Message.estimated_token_count` already prices `image_url` (by detail) and
  `input_audio` parts; `Agent._incoming_token_count` only understands `Prompt`/`str`.
- `dandy/shared/media.py` maps base64 signatures to audio/image mime types;
  `shared/files.py` has `encode_file_to_base64`.
- `DandyCli` (`dandy/interfaces/cli/cli.py`): `process_user_input(str)` →
  `process_agent_input(user_input: str)` → `tui.printer.run_timed_task` running
  `agent.turn(user_input, ...)`. Sessions save `last_request` as a string.
- `MessageHistory` messages serialize to the OpenAI wire shape; the strict-endpoint
  gotcha forbids multiple/leading system messages (user messages are fine).
- Tests: `tests/interfaces/cli/test_tui.py` (VT-emulator screen tests, incl.
  `TestTuiMultiLineInput`), `tests/application/agent/test_agent.py` (mocked
  `request_to_response`). Hermetic by default.

## Plan

1. **TUI: atomic bracketed paste + `/paste` fallback command**
   - Enable bracketed paste mode for the duration of the input loop
     (`try/finally` around the `cbreak` loop).
   - Detect the `ESC[200~` start (buffer the `200~` tail with a short
     `inkey(timeout=...)`; on timeout, flush the buffered bytes as ordinary keys).
     While inside a paste, swallow everything verbatim — newlines included — into
     a paste block; `ESC[201~` (same buffering) closes it.
   - Model the buffer as a list of blocks: char blocks (as today) and paste blocks
     (full text). `_render` shows a paste block as a compact indicator
     (`⤶ 12 lines · 3.4 KB pasted`); the submitted value is the verbatim join.
     Backspace deletes the last block/char. Existing single-line render, wrap,
     and suggestion behavior is untouched for char blocks.
   - Add a `/paste` (`/p`) command to the `CLI_COMMANDS` registry for terminals
     without bracketed paste: it reads stdin lines until EOF (Ctrl-D) and submits
     them as one message. `one_shot.py`/usage pick it up from the registry
     automatically.
   - Done when `test_tui.py` screen tests cover: a scripted paste burst with
     newlines arrives as one message; a split `ESC[200`/`~` sequence is still
     recognized; a stray `ESC [ 2 0 0 ~` typed by hand (no paste) still behaves
     like ordinary keys after the timeout flush; and all existing tests pass.

2. **Attachment model (application layer, new module
   `dandy/application/agent/attachments.py`)**
   - `TurnAttachment` dataclass: `source_path: Path`, `kind`
     (`image` | `audio` | `project_file`), `delivery_path: Path | None` (the copy
     for `project_file`). Constants for the image/audio extensions.
   - `detect_attachment_paths(text, base_path) -> (remaining_text, list[Path])`:
     pull path-like tokens (no whitespace, not a URL) out of the text, expand `~`,
     keep the ones that exist; strip the tokens (preserving surrounding text),
     resolve relative paths against `base_path` (the project root).
   - `prepare_turn_attachments(paths, base_path) -> (list[TurnAttachment], list[issue_str])`:
     classify image/audio by extension; copy every other existing file into
     `<base>/.dandy/attachments/<UTC timestamp>__<name>` (collisions get a
     suffix); unreadable/failed copies become an issue string, never an exception.
   - Done when `tests/application/agent/test_attachments.py` covers detection
     (URLs ignored, `~` expanded, relative + absolute, missing paths ignored,
     surrounding text preserved), classification, copy-once + collision naming,
     and copy-failure issues, on temp dirs.

3. **`Agent.turn` accepts attachments and builds one multimodal user message**
   - `Agent.turn(message=..., attachments: list[TurnAttachment] | None = None)`.
   - When attachments exist, the turn builds a `Message(role='user')` with a text
     part plus `add_content_from_image_file_path` /
     `add_content_from_input_audio_file_path` parts for image/audio attachments,
     and appends one text line per `project_file` attachment naming its
     `delivery_path`; that message is added directly to `self.history` before the
     tool loop, and the tool loop is called with `prompt=None`. No attachments →
     today's code path, byte-for-byte.
   - `last_request` stays a plain string (the text part), so sessions are
     unchanged; `_incoming_token_count` learns the attachment token math
     (text + per-image detail tokens + per-audio estimate, reusing
     `dandy/domain/tokens/estimate`).
   - Done when `tests/application/agent/test_agent.py` gains hermetic cases
     (mocked `request_to_response`): the outgoing request body carries one user
     message with text + image parts; project-file paths appear in the text; the
     token-fit check prices images; the no-attachment path is unchanged.

4. **CLI wiring**
   - `Tui.get_user_input` returns the submitted text; `DandyCli` runs
     `detect_attachment_paths` + `prepare_turn_attachments` before the turn,
     prints one line per attachment (`Attached "screenshot.png" (image)` /
     `Saved "notes.txt" → .dandy/attachments/...`) and one per issue, then
     `agent.turn(remaining_text, attachments=...)`.
   - `process_agent_input` / `run_in_session` / `run_new_one_shot` thread the
     attachments through; the `run_timed_task` header keeps
     `user_input[:80]`.
   - Done when `tests/interfaces/cli/test_cli.py` covers the wiring on a stubbed
     turn: image paths arrive as attachments, other files are copied and their
     delivery paths reach the agent, and one-shot `--new "<img>"` behaves the
     same.

5. **Docs + AGENTS.md**
   - `docs/user_guide/` CLI page: bracketed paste, the `/paste` fallback, and
     file attachment behavior; `docs/changelog/v3.md` entry; AGENTS.md CLI
     section paragraph.
   - Done when `just docs-tests` passes.

6. **Full verification**
   - `just test`, `ruff check .`, `ruff format --check .`, `just lint-imports`,
     `just docs-tests`.
   - Done when all four report clean.

## Completion Test

1. `PYTHONPATH=. python -m pytest tests/interfaces/cli/test_tui.py tests/application/agent/ tests/interfaces/cli/test_cli.py -q` → all pass.
2. `just test` → whole suite green (hermetic).
3. `ruff check . && ruff format --check . && just lint-imports && just docs-tests` → clean.
4. Screen-level: a scripted bracketed-paste burst (`ESC[200~line1\nline2\nESC[201~`,
   including a mid-sequence split across two `inkey` yields) followed by Enter
   produces exactly one submitted message containing both lines, with the
   indicator shown while typing — asserted in the VT-emulator tests.

## Deviations

none yet
