from typing import Callable

from dandy.application.agent.agent import (
    AGENT_COMPACTION_TARGET_RATIO,
    AGENT_MAX_CONTEXT_TOKENS_DEFAULT,
)
from dandy.application.agent.bots.coding_bot import CodingBot
from dandy.application.agent.bots.planning_bot import PlanningBot
from dandy.application.agent.exceptions import AgentRecoverableError
from dandy.application.agent.tools import AGENT_TOOLS
from dandy.shared.settings import settings
from dandy.domain.intel.intel import DefaultIntel
from dandy.domain.prompt.prompt import Prompt
from dandy.domain.message.message import MessageHistory, compact_message_history
from dandy.domain.tokens.estimate import get_estimated_token_count_for_string


class CodingAgent:
    """Multi-turn coding agent that keeps the conversation across chat calls."""

    def __init__(self, run_planning: bool = True) -> None:
        self.run_planning = run_planning
        self.planning_bot = PlanningBot()
        self.bot = CodingBot()
        self.history = MessageHistory()
        self.max_context_tokens = self._resolve_context_size()

    def _resolve_context_size(self) -> int:
        """The coding LLM config's ``CONTEXT_SIZE``, or a safe default."""
        llm_configs = getattr(settings, 'LLM_CONFIGS', None)

        if isinstance(llm_configs, dict):
            for config_name in (self.bot.llm_config, 'DEFAULT'):
                config = llm_configs.get(config_name)

                if not isinstance(config, dict):
                    continue

                candidate = config.get('CONTEXT_SIZE')

                try:
                    context_size = int(candidate) if candidate else 0
                except (TypeError, ValueError):
                    context_size = 0

                if context_size > 0:
                    return context_size

        return AGENT_MAX_CONTEXT_TOKENS_DEFAULT

    def chat(
        self,
        user_input: str,
        progress_callback: Callable[[str], None] | None = None,
        verbose_callback: Callable[[str], None] | None = None,
    ) -> DefaultIntel:
        plan_intel = self._create_plan(user_input, progress_callback, verbose_callback)
        prompt: Prompt | str = user_input

        if plan_intel is not None:
            prompt = (
                Prompt()
                .text(user_input)
                .line_break()
                .heading('Implementation Plan')
                .line_break()
                .intel(plan_intel)
            )

        self._compact_history_for_next_message(prompt=prompt, progress_callback=progress_callback)
        self._ensure_history_fits(prompt)

        return self.bot.llm.tools.prompt_to_intel(
            prompt=prompt,
            tools=AGENT_TOOLS,
            intel_class=DefaultIntel,
            message_history=self.history,
            replace_message_history=True,
            progress_callback=progress_callback,
            verbose_callback=verbose_callback,
            max_tool_iterations=None,
        )

    def _create_plan(
        self,
        user_input: str,
        progress_callback: Callable[[str], None] | None = None,
        verbose_callback: Callable[[str], None] | None = None,
    ) -> DefaultIntel | None:
        if not self.run_planning:
            return None

        # Every chat gets a fresh planning conversation: the coding history
        # already carries the full context, and prior chats' plans only add
        # stale material to the new plan.
        self.planning_bot.reset()

        if progress_callback is not None:
            progress_callback('Planning')

        return self.planning_bot.llm.tools.prompt_to_intel(
            prompt=user_input,
            tools=AGENT_TOOLS,
            intel_class=DefaultIntel,
            progress_callback=progress_callback,
            verbose_callback=verbose_callback,
            max_tool_iterations=None,
        )

    def _compaction_target_token_count(self) -> int:
        """A fraction of the max context, reserving headroom for output."""
        return max(1, int(self.max_context_tokens * AGENT_COMPACTION_TARGET_RATIO))

    def _incoming_token_count(self, prompt: Prompt | str) -> int:
        if isinstance(prompt, Prompt):
            return prompt.estimated_token_count

        return get_estimated_token_count_for_string(prompt)

    def _compact_history_for_next_message(
        self, prompt: Prompt | str, progress_callback: Callable[[str], None] | None = None
    ) -> None:
        incoming_token_count = self._incoming_token_count(prompt)
        target_token_count = max(1, self._compaction_target_token_count() - incoming_token_count)
        current_token_count = self.history.estimated_token_count

        if current_token_count <= target_token_count:
            return

        if progress_callback is not None:
            progress_callback(f'Compacting conversation history ({current_token_count} tokens)...')

        compact_message_history(history=self.history, max_context_tokens=target_token_count)

    def _ensure_history_fits(self, prompt: Prompt | str) -> None:
        """Fail clearly when compaction could not bring the conversation under the window.

        Compaction drops everything it can drop and then gives up without
        raising; when what remains still exceeds the whole context window no
        valid request can be built, so the CLI shows this instead of an
        opaque provider 400.
        """
        total_token_count = self.history.estimated_token_count + self._incoming_token_count(prompt)

        if total_token_count <= self.max_context_tokens:
            return

        message = (
            f'The conversation ({self.history.estimated_token_count} tokens) plus your '
            f'message still exceeds the {self.max_context_tokens} token context window '
            'after dropping everything droppable. Clear the conversation and retry, '
            'with a shorter message if possible.'
        )
        raise AgentRecoverableError(message)

    def clear(self) -> None:
        self.history = MessageHistory()
        self.planning_bot.reset()
        self.bot.reset()
