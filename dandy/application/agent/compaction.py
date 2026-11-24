from dandy.shared.exceptions import RunStoppedError
from dandy.domain.message.compaction import (
    compact_message_history,
    replace_middle_with_summary,
    summarizable_middle_range,
)
from dandy.domain.message.message import Message, MessageHistory

_MIDDLE_MESSAGE_CHARACTER_LIMIT = 1200


def summarize_and_compact_history(history: MessageHistory, max_context_tokens: int) -> bool:
    """Fold the older middle of ``history`` into one summary message.

    The system slot, the opening exchange, and the newest rounds are kept
    verbatim; everything between is summarized by a fast bot and replaced by a
    single summary message. Returns ``True`` when a summary replaced the middle.
    When there is nothing to summarize, or the summarizer fails, the drop-only
    ``compact_message_history`` runs instead and ``False`` is returned, so the
    loop is never blocked. A user stop is re-raised, not swallowed.
    """
    head_end_index, tail_start_index = summarizable_middle_range(history)

    if tail_start_index <= head_end_index:
        compact_message_history(history, max_context_tokens)
        return False

    middle_messages = history.messages[head_end_index:tail_start_index]

    try:
        from dandy.application.agent.intelligence.bots.compaction_bot import (  # noqa: PLC0415
            CompactionBot,
        )

        summary_intel = CompactionBot().process(_messages_to_text(middle_messages))
        summary_message = Message(role='user')
        summary_message.add_content_from_text(summary_intel.to_summary_text())
    except RunStoppedError:
        raise
    except Exception:
        compact_message_history(history, max_context_tokens)
        return False

    replace_middle_with_summary(history, head_end_index, tail_start_index, summary_message)

    return True


def _messages_to_text(messages: list[Message]) -> str:
    lines = []

    for message in messages:
        if message.tool_calls:
            for tool_call in message.tool_calls:
                function = tool_call.get('function') or {}
                arguments = _clip(str(function.get('arguments', '')))
                lines.append(f'assistant called {function.get("name", "?")} ({arguments})')
        elif message.role == 'tool':
            lines.append(f'tool result: {_clip(message.text_content)}')
        elif message.text_content:
            lines.append(f'{message.role}: {_clip(message.text_content)}')

    return '\n'.join(lines)


def _clip(text: str) -> str:
    if len(text) <= _MIDDLE_MESSAGE_CHARACTER_LIMIT:
        return text

    return text[:_MIDDLE_MESSAGE_CHARACTER_LIMIT] + '...'
