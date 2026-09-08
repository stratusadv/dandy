from typing import Callable

from dandy.cli.intelligence.bots.coding_bot import CodingBot
from dandy.cli.intelligence.bots.planning_bot import PlanningBot
from dandy.cli.intelligence.tools import AGENT_TOOLS
from dandy.conf import settings
from dandy.intel.intel import DefaultIntel
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.request.message import MessageHistory, compact_message_history
from dandy.llm.tokens.utils import get_estimated_token_count_for_string

AGENT_MAX_CONTEXT_TOKENS_DEFAULT = 65536
AGENT_COMPACTION_TARGET_RATIO = 0.70


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
        self._compact_history_for_next_message(
            user_input=user_input, progress_callback=progress_callback
        )

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

    def _compact_history_for_next_message(
        self, user_input: str, progress_callback: Callable[[str], None] | None = None
    ) -> None:
        incoming_token_count = get_estimated_token_count_for_string(user_input)
        target_token_count = max(1, self._compaction_target_token_count() - incoming_token_count)
        current_token_count = self.history.estimated_token_count

        if current_token_count <= target_token_count:
            return

        if progress_callback is not None:
            progress_callback(f'Compacting conversation history ({current_token_count} tokens)...')

        compact_message_history(history=self.history, max_context_tokens=target_token_count)

    def clear(self) -> None:
        self.history = MessageHistory()
        self.planning_bot.reset()
        self.bot.reset()
