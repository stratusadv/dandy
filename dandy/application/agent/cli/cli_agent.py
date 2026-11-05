from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from dandy.application.agent.agent import AGENT_MAX_TOOL_ROUNDS_DEFAULT, Agent
from dandy.application.agent.cli.agents_md import read_agents_md
from dandy.application.agent.cli.intelligence.bots.coding_bot import CodingBot
from dandy.application.agent.cli.intelligence.bots.init_bot import InitBot
from dandy.application.agent.cli.intelligence.prompts import init_prompt
from dandy.application.agent.session import session
from dandy.application.agent.intelligence.tools import AGENT_TOOLS
from dandy.application.agent.intelligence.tools.question import QuestionHandler, QuestionTool
from dandy.domain.intel.intel import DefaultIntel
from dandy.domain.message.message import MessageContent

if TYPE_CHECKING:
    from dandy.domain.tool.beat import StoryBeat


class CliAgent(Agent):
    """Multi-turn coding agent that keeps the conversation across turns."""

    def __init__(self, ask_user: QuestionHandler | None = None) -> None:
        super().__init__(
            bot=CodingBot(),
            tools=[*AGENT_TOOLS, QuestionTool(ask_user=ask_user)],
            intel_class=DefaultIntel,
        )

    def reload_agents_md(self) -> str:
        """Re-read the project AGENTS.md and sync it into the system prompt.

        Rebuilds the bot's guidelines, the connector's system message, and the
        running conversation's system message (when one exists), so a
        regenerated AGENTS.md applies to the next turn without a /new.
        Returns the refreshed system prompt text.
        """
        self.bot.guidelines = self.bot.build_guidelines()
        system_prompt = self.bot.llm.rebuild_system_prompt()

        if self.history.has_system_message:
            self.history.messages[0].content = [MessageContent(type='text', text=system_prompt)]

        return system_prompt

    def run_init_pass(
        self,
        progress_callback: Callable[[StoryBeat], None] | None = None,
        verbose_callback: Callable[[str], None] | None = None,
    ) -> str | None:
        """Run the AGENTS.md generation pass in a fresh InitBot conversation.

        The bot explores the project and writes (or refreshes) AGENTS.md at
        the project root, reading the existing file from the prompt when one
        exists. On success the coding agent's system prompt is reloaded from
        the file. Returns the bot's summary text, or None when the file was
        not written.
        """
        init_bot = InitBot()

        result_intel: DefaultIntel = init_bot.llm.tools.prompt_to_intel(
            prompt=init_prompt(read_agents_md(session.agents_md_path)),
            tools=AGENT_TOOLS,
            intel_class=DefaultIntel,
            progress_callback=progress_callback,
            verbose_callback=verbose_callback,
            max_tool_iterations=AGENT_MAX_TOOL_ROUNDS_DEFAULT,
        )

        if not session.agents_md_path.is_file():
            return None

        self.reload_agents_md()

        return result_intel.text

    def clear(self) -> None:
        super().clear()
