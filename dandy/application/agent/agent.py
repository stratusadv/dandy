from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from dandy.application.agent.exceptions import AgentCriticalError, AgentRecoverableError
from dandy.application.agent.intel import AgentSession, AgentTurnIntel
from dandy.application.agent.prompts import continuation_prompt
from dandy.domain.message.message import MessageHistory, compact_message_history
from dandy.domain.prompt.prompt import Prompt
from dandy.domain.skill.skill import to_skill_instances
from dandy.domain.tokens.estimate import get_estimated_token_count_for_string

if TYPE_CHECKING:
    from dandy.application.bot.bot import Bot
    from dandy.domain.intel.typing import IntelType
    from dandy.domain.skill.skill import SkillType
    from dandy.domain.tool.tool import ToolType

AGENT_MAX_CONTEXT_TOKENS_DEFAULT = 65536
AGENT_COMPACTION_TARGET_RATIO = 0.70


class Agent:
    """A stateful agent built around a Bot, designed to be looped.

    A turn is one exchange: a message goes in, the agent works (possibly across
    many tool rounds), and a final answer comes out; the conversation
    accumulates in the agent's history. run drives turns until the agent's
    result signals the request is done or the turn budget is exhausted.
    """

    def __init__(
        self,
        bot: Bot,
        tools: list[ToolType] | None = None,
        skills: list[SkillType] | None = None,
        max_turns: int | None = None,
        intel_class: type[IntelType] | None = None,
    ) -> None:
        self.bot = bot
        self.tools = tools
        self.skills = to_skill_instances(skills)
        self.max_turns = max_turns
        self.intel_class = intel_class or AgentTurnIntel
        self.history = MessageHistory()
        self.max_context_tokens = self._resolve_context_size()
        self.last_request: str | None = None

        if self.skills:
            self.bot.llm.skills.register(self.skills)
            self.bot.llm.append_system_prompt(self.bot.llm.skills.system_prompt_section())

    def _resolve_context_size(self) -> int:
        """The bot's LLM config ``CONTEXT_SIZE``, or a safe default."""
        context_size = self.bot.llm.config.context_size
        return context_size if context_size > 0 else AGENT_MAX_CONTEXT_TOKENS_DEFAULT

    def turn(
        self,
        message: Prompt | str | None = None,
        progress_callback: Callable[[str], None] | None = None,
        verbose_callback: Callable[[str], None] | None = None,
    ) -> IntelType:
        """Run one exchange: prepare, compact, work through any tool rounds, return the answer.

        The conversation accumulates in ``self.history`` across turns.
        """
        self.last_request = self._message_as_str(message)
        message = self._prepare_message(message, progress_callback, verbose_callback)
        self._compact_history_for_next_message(message, progress_callback)
        self._ensure_history_fits(message)

        return self.bot.llm.tools.prompt_to_intel(
            prompt=message,
            tools=self.tools,
            intel_class=self.intel_class,
            message_history=self.history,
            replace_message_history=True,
            progress_callback=progress_callback,
            verbose_callback=verbose_callback,
            max_tool_iterations=None,
        )

    def _prepare_message(
        self,
        message: Prompt | str | None,
        _progress_callback: Callable[[str], None] | None = None,
        _verbose_callback: Callable[[str], None] | None = None,
    ) -> Prompt | str | None:
        """Subclass hook to shape the incoming message before it goes to the bot."""
        return message

    def _ensure_history_fits(self, message: Prompt | str | None) -> None:
        """Fail clearly when compaction could not bring the conversation under the window.

        Compaction drops everything it can drop and then gives up without
        raising; when what remains still exceeds the whole context window no
        valid request can be built, so callers see this instead of an opaque
        provider 400.
        """
        total_token_count = self.history.estimated_token_count + self._incoming_token_count(message)

        if total_token_count <= self.max_context_tokens:
            return

        error_message = (
            f'The conversation ({self.history.estimated_token_count} tokens) plus your '
            f'message still exceeds the {self.max_context_tokens} token context window '
            'after dropping everything droppable. Clear the conversation and retry, '
            'with a shorter message if possible.'
        )
        raise AgentRecoverableError(error_message)

    def run(
        self,
        request: Prompt | str,
        is_done: Callable[[IntelType], bool] | None = None,
        progress_callback: Callable[[str], None] | None = None,
        verbose_callback: Callable[[str], None] | None = None,
    ) -> IntelType:
        """Drive turns until the request is complete or the turn budget is exhausted.

        The first turn receives the request; later turns receive a
        continuation nudge. Completion comes from ``is_done(result)`` when
        given, otherwise from a ``done`` field on the turn result.
        """
        if is_done is None and not self._has_done_field():
            message = (
                f'Agent.run cannot tell when the request is complete: '
                f'{self.intel_class.__name__} has no `done` field and no `is_done` '
                f'callback was given.'
            )
            raise AgentCriticalError(message)

        result = self.turn(
            request, progress_callback=progress_callback, verbose_callback=verbose_callback
        )
        turn_count = 1

        while not self._is_done(result, is_done):
            if self.max_turns is not None and turn_count >= self.max_turns:
                message = (
                    f'Agent gave up after {self.max_turns} turns without the request '
                    f'being complete.'
                )
                raise AgentRecoverableError(message)

            result = self.turn(
                continuation_prompt(),
                progress_callback=progress_callback,
                verbose_callback=verbose_callback,
            )
            turn_count += 1

        return result

    def clear(self) -> None:
        """Reset the conversation history and the bot."""
        self.history = MessageHistory()
        self.last_request = None
        self.bot.reset()

    def save_session(self) -> AgentSession:
        """Snapshot the conversation and LLM context for later loading."""
        return AgentSession(
            messages=list(self.history.messages),
            last_request=self.last_request,
            model=self.bot.llm.config.model,
            config=self.bot.llm.config.name,
            token_count=self.history.estimated_token_count,
        )

    def load_session(self, session: AgentSession) -> None:
        """Replace the conversation with a saved snapshot and reset the bot."""
        self.history = MessageHistory(messages=list(session.messages))
        self.last_request = session.last_request
        self.bot.reset()

    def _has_done_field(self) -> bool:
        return 'done' in getattr(self.intel_class, 'model_fields', {})

    def _is_done(self, result: IntelType, is_done: Callable[[IntelType], bool] | None) -> bool:
        if is_done is not None:
            return bool(is_done(result))

        return bool(getattr(result, 'done', False))

    def _message_as_str(self, message: Prompt | str | None) -> str | None:
        if message is None:
            return None

        if isinstance(message, Prompt):
            return message.to_str()

        return message

    def _incoming_token_count(self, message: Prompt | str | None) -> int:
        if message is None:
            return 0

        if isinstance(message, Prompt):
            return message.estimated_token_count

        return get_estimated_token_count_for_string(message)

    def _compaction_target_token_count(self) -> int:
        """A fraction of the max context, reserving headroom for output."""
        return max(1, int(self.max_context_tokens * AGENT_COMPACTION_TARGET_RATIO))

    def _compact_history_for_next_message(
        self, message: Prompt | str | None, progress_callback: Callable[[str], None] | None = None
    ) -> None:
        incoming_token_count = self._incoming_token_count(message)
        target_token_count = max(1, self._compaction_target_token_count() - incoming_token_count)
        current_token_count = self.history.estimated_token_count

        if current_token_count <= target_token_count:
            return

        if progress_callback is not None:
            progress_callback(f'Compacting conversation history ({current_token_count} tokens)...')

        compact_message_history(history=self.history, max_context_tokens=target_token_count)
