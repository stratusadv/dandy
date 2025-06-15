import json

from pydantic import ValidationError

from dandy.core.utils import pydantic_validation_error_to_str, pascal_to_title_case
from dandy.recorder.recorder import Recorder
from dandy.intel import BaseIntel
from dandy.llm.service.request.request import BaseRequestBody
from dandy.llm.tokens.utils import get_estimated_token_count_for_string
from dandy.recorder.events import Event, EventAttribute, EventType

_EVENT_OBJECT_NAME = 'LLM Agent'


def recorder_add_llm_agent_event(
        action_description: str,
        event_id: str
):
    Recorder.add_event(
        Event(
            id=event_id,
            object_name=_EVENT_OBJECT_NAME,
            callable_name=action_description,
            type=EventType.OTHER,
            attributes=[
                EventAttribute(
                    key='Something',
                    value='Something',
                )
            ]
        )
    )


