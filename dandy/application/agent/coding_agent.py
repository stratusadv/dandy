from __future__ import annotations

from typing import Callable

from dandy.application.agent.agent import Agent
from dandy.application.agent.bots.coding_bot import CodingBot
from dandy.application.agent.bots.planning_bot import PlanningBot
from dandy.application.agent.tools import AGENT_TOOLS
from dandy.domain.intel.intel import DefaultIntel
from dandy.domain.prompt.prompt import Prompt


class CodingAgent(Agent):
    """Multi-turn coding agent that keeps the conversation across turns."""

    def __init__(self, run_planning: bool = True) -> None:
        super().__init__(bot=CodingBot(), tools=AGENT_TOOLS, intel_class=DefaultIntel)
        self.run_planning = run_planning
        self.planning_bot = PlanningBot()

    def _prepare_message(
        self,
        message: Prompt | str | None,
        progress_callback: Callable[[str], None] | None = None,
        verbose_callback: Callable[[str], None] | None = None,
    ) -> Prompt | str | None:
        if message is None or not self.run_planning:
            return message

        plan_intel = self._create_plan(message, progress_callback, verbose_callback)

        return (
            Prompt()
            .text(message.to_str() if isinstance(message, Prompt) else message)
            .line_break()
            .heading('Implementation Plan')
            .line_break()
            .intel(plan_intel)
        )

    def _create_plan(
        self,
        message: Prompt | str,
        progress_callback: Callable[[str], None] | None = None,
        verbose_callback: Callable[[str], None] | None = None,
    ) -> DefaultIntel:
        # Every turn gets a fresh planning conversation: the coding history
        # already carries the full context, and prior turns' plans only add
        # stale material to the new plan.
        self.planning_bot.reset()

        if progress_callback is not None:
            progress_callback('Planning')

        return self.planning_bot.llm.tools.prompt_to_intel(
            prompt=message,
            tools=AGENT_TOOLS,
            intel_class=DefaultIntel,
            progress_callback=progress_callback,
            verbose_callback=verbose_callback,
            max_tool_iterations=None,
        )

    def clear(self) -> None:
        super().clear()
        self.planning_bot.reset()
