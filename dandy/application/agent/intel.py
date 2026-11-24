from datetime import datetime

from pydantic import Field

from dandy.domain.intel.intel import BaseIntel
from dandy.domain.message.message import Message


class AgentTurnIntel(BaseIntel):
    text: str
    done: bool = False


class AgentSession(BaseIntel):
    """A snapshot of an agent's conversation and LLM context at one moment."""

    messages: list[Message] = Field(default_factory=list)
    last_request: str | None = None
    model: str | None = None
    config: str | None = None
    token_count: int = 0


class SessionRecord(BaseIntel):
    """A named, timestamped AgentSession as stored on disk."""

    name: str
    created_at: datetime
    updated_at: datetime
    session: AgentSession


class SessionNameIntel(BaseIntel):
    """The AI-generated title used to name a new session."""

    name: str


class CompactionSummaryIntel(BaseIntel):
    """A compact structured summary of the older part of a conversation."""

    goal: str
    key_decisions: list[str] = Field(default_factory=list)
    files_touched: list[str] = Field(default_factory=list)
    commands_run: list[str] = Field(default_factory=list)
    errors_and_fixes: list[str] = Field(default_factory=list)
    pending_tasks: list[str] = Field(default_factory=list)
    current_work: str = ''
    next_step: str = ''

    def to_summary_text(self) -> str:
        lines = ['[Summary of earlier conversation]', f'Goal: {self.goal}']

        for heading, items in (
            ('Key decisions', self.key_decisions),
            ('Files touched', self.files_touched),
            ('Commands run', self.commands_run),
            ('Errors and fixes', self.errors_and_fixes),
            ('Pending tasks', self.pending_tasks),
        ):
            if items:
                lines.append(f'{heading}:')
                lines.extend(f'- {item}' for item in items)

        if self.current_work:
            lines.append(f'Current work: {self.current_work}')

        if self.next_step:
            lines.append(f'Next step: {self.next_step}')

        return '\n'.join(lines)
