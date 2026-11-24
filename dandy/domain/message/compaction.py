from dandy.domain.message.message import Message, MessageHistory
from dandy.domain.tokens.estimate import TOKEN_COUNT_REQUEST_OVERHEAD

# Fallback context window in tokens when the LLM config has no CONTEXT_SIZE.
DEFAULT_CONTEXT_WINDOW = 65536

# Compaction trims the history down to this share of the context window,
# leaving the rest as headroom for the completion.
COMPACTION_TARGET_RATIO = 0.70

# Compaction triggers at this higher share of the window and compacts back
# down to the target, so a loop whose rounds keep re-adding about what
# compaction just dropped does not re-compact on every round.
COMPACTION_TRIGGER_RATIO = 0.80

# When summarizing, the newest rounds up to this many tokens are kept verbatim
# so the model continues seamlessly; everything older folds into the summary.
COMPACTION_RECENT_TAIL_TOKENS = 16384


def compact_message_history(history: MessageHistory, max_context_tokens: int) -> None:
    """Trim ``history`` until its estimated token count fits the budget.

    The message in the system slot (position 0) is always kept, as is the
    opening exchange: the first user message is the original request, and
    dropping it leaves the model working toward a goal it can no longer see.
    When the opening exchange is a tool-use round, its assistant declaration
    and tool results are protected along with it. The newest message is kept
    unless it is a ``tool`` result: when the newest message is a tool result,
    its whole round (the assistant tool-call declaration plus all its results)
    is dropped, because a tool result without its declaration is invalid on
    the wire. Tool-use rounds are dropped oldest first because they consume
    the most tokens, then oldest plain exchanges.

    Does not raise when the history cannot be brought under budget, it simply
    drops everything droppable.
    """
    per_message_token_counts = [message.estimated_token_count for message in history.messages]
    total_token_count = TOKEN_COUNT_REQUEST_OVERHEAD + sum(per_message_token_counts)

    while total_token_count > max_context_tokens:
        start_index, end_index = _oldest_droppable_range(history)

        if start_index is None or end_index is None:
            return

        total_token_count -= sum(per_message_token_counts[start_index:end_index])

        del per_message_token_counts[start_index:end_index]
        del history.messages[start_index:end_index]


def drop_incomplete_tool_round(history: MessageHistory) -> None:
    """Drop the trailing tool round when its results never all arrived.

    A crash mid round leaves an assistant tool-call declaration followed by
    fewer tool results than declared calls (possibly none); replaying that
    round is invalid on the wire, so the whole round is dropped and the
    conversation ends at the last complete exchange. Complete conversations
    are untouched.
    """
    messages = history.messages

    if not messages:
        return

    last_index = len(messages) - 1
    last_message = messages[last_index]

    if last_message.role == 'tool':
        declaration_index = last_index

        while declaration_index >= 0 and messages[declaration_index].role == 'tool':
            declaration_index -= 1

        if (
            declaration_index < 0
            or messages[declaration_index].role != 'assistant'
            or not messages[declaration_index].tool_calls
        ):
            return

        result_ids = {
            message.tool_call_id for message in messages[declaration_index + 1 : last_index + 1]
        }
    elif last_message.role == 'assistant' and last_message.tool_calls:
        declaration_index = last_index
        result_ids = set()
    else:
        return

    declaration = messages[declaration_index]
    declared_ids = {tool_call.get('id') for tool_call in declaration.tool_calls}

    if declared_ids <= result_ids:
        return

    del history.messages[declaration_index : last_index + 1]


def _opening_exchange_end_index(history: MessageHistory) -> int:
    """Return the index just past the opening exchange, which compaction never drops.

    The first user message is the original request; dropping it leaves the
    model working on a goal it can no longer see. When that exchange is a
    tool-use round, the assistant declaration and its tool results are
    protected as well, so the kept prefix stays valid on the wire.
    """
    messages = history.messages

    for index in range(len(messages)):
        if messages[index].role != 'user':
            continue

        end_index = index + 1

        if (
            end_index < len(messages)
            and messages[end_index].role == 'assistant'
            and messages[end_index].tool_calls
        ):
            end_index += 1
            while end_index < len(messages) and messages[end_index].role == 'tool':
                end_index += 1

        return end_index

    return 0


def _oldest_droppable_range(history: MessageHistory) -> tuple[int | None, int | None]:
    messages = history.messages

    if len(messages) < 2:
        return None, None

    last_index = len(messages) - 1
    opening_end_index = _opening_exchange_end_index(history)

    if opening_end_index >= last_index:
        return None, None

    for index in range(opening_end_index, last_index):
        message = messages[index]

        if message.role != 'assistant' or not message.tool_calls:
            continue

        end_index = index + 1

        while end_index < len(messages) and messages[end_index].role == 'tool':
            end_index += 1

        return index, end_index

    for index in range(opening_end_index, last_index):
        message = messages[index]

        if message.role == 'user':
            return index, index + 1

        if message.role == 'assistant' and not message.tool_calls:
            return index, index + 1

    return None, None


def summarizable_middle_range(
    history: MessageHistory, recent_tail_tokens: int = COMPACTION_RECENT_TAIL_TOKENS
) -> tuple[int, int]:
    """Bound the summarizable middle as ``(head_end_index, tail_start_index)``.

    The head is the system slot plus the opening exchange; the tail is the
    newest rounds up to ``recent_tail_tokens``, cut at a round boundary so it
    stays wire-valid on its own. When there is nothing to summarize the two
    indices meet and the middle is empty.
    """
    head_end_index = _opening_exchange_end_index(history)
    tail_start_index = _recent_tail_start_index(history, recent_tail_tokens)

    tail_start_index = max(tail_start_index, head_end_index)

    return head_end_index, tail_start_index


def replace_middle_with_summary(
    history: MessageHistory, head_end_index: int, tail_start_index: int, summary_message: Message
) -> None:
    """Replace the middle of ``history`` with one summary message, keeping head and tail."""
    history.messages = [
        *history.messages[:head_end_index],
        summary_message,
        *history.messages[tail_start_index:],
    ]


def _recent_tail_start_index(history: MessageHistory, recent_tail_tokens: int) -> int:
    messages = history.messages

    if not messages:
        return 0

    total_token_count = 0
    start_index = len(messages)

    for index in range(len(messages) - 1, -1, -1):
        total_token_count += messages[index].estimated_token_count

        if total_token_count > recent_tail_tokens:
            break

        if messages[index].role in ('user', 'assistant'):
            start_index = index

    if start_index == len(messages):
        for index in range(len(messages) - 1, -1, -1):
            if messages[index].role in ('user', 'assistant'):
                return index

    return start_index
