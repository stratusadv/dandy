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
