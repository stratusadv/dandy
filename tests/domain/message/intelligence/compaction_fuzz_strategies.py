from hypothesis import strategies
from hypothesis.strategies import DrawFn, composite

from dandy.domain.message.message import MessageHistory

_SMALL_MESSAGE_TEXT = strategies.text(alphabet='abcdef ghij', min_size=0, max_size=4000)


def _large_message_text(character_count: int) -> str:
    return 'x' * character_count


_LARGE_MESSAGE_TEXT = strategies.integers(min_value=10_000, max_value=20_000).map(
    _large_message_text
)
MESSAGE_TEXT = strategies.one_of(
    _SMALL_MESSAGE_TEXT, _SMALL_MESSAGE_TEXT, _SMALL_MESSAGE_TEXT, _LARGE_MESSAGE_TEXT
)
TOOL_CALL_NAMES = ['get_weather', 'read_file', 'run_command']


@composite
def conversation_history_strategy(draw: DrawFn) -> MessageHistory:
    history = MessageHistory()
    history.add_message(role='system', text=draw(MESSAGE_TEXT))

    round_count = draw(strategies.integers(min_value=0, max_value=5))

    for round_index in range(round_count):
        is_final_round = round_index == round_count - 1

        if draw(strategies.booleans()):
            _add_tool_round(history, draw, round_index, allow_unfinished=is_final_round)
        else:
            _add_plain_round(history, draw)

    return history


@composite
def fuzz_budget_strategy(draw: DrawFn) -> int:
    return draw(strategies.integers(min_value=0, max_value=100_000))


def _add_plain_round(history: MessageHistory, draw: DrawFn) -> None:
    history.add_message(role='user', text=draw(MESSAGE_TEXT))

    if draw(strategies.booleans()):
        history.add_message(role='assistant', text=draw(MESSAGE_TEXT))


def _add_tool_round(
    history: MessageHistory, draw: DrawFn, round_index: int, allow_unfinished: bool = False
) -> None:
    if draw(strategies.booleans()):
        history.add_message(role='user', text=draw(MESSAGE_TEXT))

    tool_call_count = draw(strategies.integers(min_value=1, max_value=3))

    tool_calls = [
        {
            'id': f'call_{round_index}_{call_index}',
            'type': 'function',
            'function': {'name': draw(strategies.sampled_from(TOOL_CALL_NAMES)), 'arguments': '{}'},
        }
        for call_index in range(tool_call_count)
    ]

    history.add_message(role='assistant', tool_calls=tool_calls)

    if allow_unfinished and draw(strategies.integers(min_value=0, max_value=4)) == 0:
        return

    for tool_call in tool_calls:
        history.add_message(role='tool', tool_call_id=tool_call['id'], text=draw(MESSAGE_TEXT))
