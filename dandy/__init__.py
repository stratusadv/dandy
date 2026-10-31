from dandy.application.agent.agent import Agent
from dandy.application.bot.bot import Bot
from dandy.application.decision.decision import Decision
from dandy.infrastructure.cache.memory.cache import MemoryCache
from dandy.infrastructure.cache.memory.decorators import cache_to_memory
from dandy.infrastructure.cache.sqlite.cache import SqliteCache
from dandy.infrastructure.cache.sqlite.decorators import cache_to_sqlite
from dandy.infrastructure.cache.key import generate_cache_key
from dandy.shared.exceptions import DandyCriticalError, DandyError, DandyRecoverableError
from dandy.infrastructure.future.process import process_to_future
from dandy.domain.intel.intel import BaseIntel, BaseListIntel, DefaultIntel
from dandy.domain.message.message import MessageHistory
from dandy.domain.prompt.prompt import Prompt
from dandy.domain.request.options import LlmOptions
from dandy.infrastructure.recorder.decorators import (
    recorder_to_html_file,
    recorder_to_json_file,
    recorder_to_markdown_file,
)
from dandy.infrastructure.recorder.recorder import Recorder
from dandy.domain.tool.tool import BaseTool
from dandy.domain.skill.skill import BaseSkill

__all__ = [
    'Agent',
    'BaseIntel',
    'BaseListIntel',
    'BaseSkill',
    'BaseTool',
    'Bot',
    'Dandy',
    'DandyCriticalError',
    'DandyError',
    'DandyRecoverableError',
    'Decision',
    'DefaultIntel',
    'LlmOptions',
    'MemoryCache',
    'MessageHistory',
    'Prompt',
    'Recorder',
    'SqliteCache',
    'cache_to_memory',
    'cache_to_sqlite',
    'generate_cache_key',
    'process_to_future',
    'recorder_to_html_file',
    'recorder_to_json_file',
    'recorder_to_markdown_file',
]


class Dandy:
    """The public Dandy API as a single namespace.

    Every public object is reachable as an attribute of this class, and it is
    the identical object the flat import gives (``Dandy.Bot`` is
    ``dandy.Bot`` — nothing is wrapped or re-created). ``from dandy import
    Dandy`` is a one-import entry point with full discoverability:
    ``Dandy.<tab>`` lists the whole API.
    """

    Agent = Agent
    BaseIntel = BaseIntel
    BaseListIntel = BaseListIntel
    BaseSkill = BaseSkill
    BaseTool = BaseTool
    Bot = Bot
    DandyCriticalError = DandyCriticalError
    DandyError = DandyError
    DandyRecoverableError = DandyRecoverableError
    Decision = Decision
    DefaultIntel = DefaultIntel
    LlmOptions = LlmOptions
    MemoryCache = MemoryCache
    MessageHistory = MessageHistory
    Prompt = Prompt
    Recorder = Recorder
    SqliteCache = SqliteCache
    cache_to_memory = cache_to_memory
    cache_to_sqlite = cache_to_sqlite
    generate_cache_key = generate_cache_key
    process_to_future = process_to_future
    recorder_to_html_file = recorder_to_html_file
    recorder_to_json_file = recorder_to_json_file
    recorder_to_markdown_file = recorder_to_markdown_file
