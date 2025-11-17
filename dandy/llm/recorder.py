import json

from pydantic import ValidationError

from dandy.core.utils import pydantic_validation_error_to_str, pascal_to_title_case
from dandy.recorder.recorder import Recorder
from dandy.intel.intel import BaseIntel
from dandy.llm.request.request import BaseRequestBody
from dandy.llm.tokens.utils import get_estimated_token_count_for_string
from dandy.recorder.events import Event, EventAttribute, EventType

_EVENT_OBJECT_NAME = 'LLM Service'


def recorder_add_llm_failure_event(
        error: Exception,
        event_id: str
):
    Recorder.add_event(
        Event(
            id=event_id,
            object_name=_EVENT_OBJECT_NAME,
            callable_name=pascal_to_title_case(error.__class__.__name__),
            type=EventType.FAILURE,
            attributes=[
                EventAttribute(
                    key='Error',
                    value=pydantic_validation_error_to_str(error) if isinstance(error, ValidationError) else str(error),
                )
            ]
        )
    )


def recorder_add_llm_retry_event(
        description: str,
        event_id: str,
        remaining_attempts: int | None = None
):
    Recorder.add_event(
        Event(
            id=event_id,
            object_name=_EVENT_OBJECT_NAME,
            callable_name='Retry',
            type=EventType.RETRY,
            attributes=[
                EventAttribute(
                    key='Reason',
                    value=f'{description}\nRemaining Attempts: {remaining_attempts}' if remaining_attempts is not None else description,
                )
            ]
        )
    )


def recorder_add_llm_request_event(
        request_body: BaseRequestBody,
        json_schema: dict,
        event_id: str
):
    llm_request_event = Event(
        id=event_id,
        object_name=_EVENT_OBJECT_NAME,
        callable_name='Request',
        type=EventType.REQUEST,
        token_usage=request_body.token_usage,
        attributes=[
            EventAttribute(
                key='Model',
                value=request_body.model
            ),
            EventAttribute(
                key='Temperature',
                value=request_body.get_temperature()
            ),
            EventAttribute(
                key='Max Context Tokens',
                value=request_body.get_total_context_length()
            ),
            EventAttribute(
                key='JSON Schema',
                value=json.dumps(json_schema, indent=4),
                is_dropdown=True,
            )
        ]
    )

    for message in request_body.messages:
        llm_request_event.add_attribute(EventAttribute(
            key=message.role,
            value=message.content_as_str(),
            is_card=True,
        ))

    Recorder.add_event(llm_request_event)

def recorder_add_llm_response_event(
        message_content: str,
        event_id: str
):
    Recorder.add_event(
        Event(
            id=event_id,
            object_name=_EVENT_OBJECT_NAME,
            callable_name='Response',
            type=EventType.RESPONSE,
            token_usage=get_estimated_token_count_for_string(message_content),
            attributes=[
                EventAttribute(
                    key='LLM Response',
                    value=message_content,
                    is_card=True,
                )
            ]
        )
    )


def recorder_add_llm_success_event(
        description: str,
        event_id: str,
        intel: BaseIntel | None = None
):
    intel_json = None

    if intel:
        intel_json = intel.model_dump_json(indent=4)

    Recorder.add_event(
        Event(
            id=event_id,
            object_name=_EVENT_OBJECT_NAME,
            callable_name='Success',
            type=EventType.SUCCESS,
            attributes=[
                EventAttribute(
                    key='Status',
                    value=description,
                ),
                EventAttribute(
                    key=intel.__class__.__name__ if intel_json else 'Result',
                    value=intel_json if intel_json else 'None',
                    is_card=True
                ),
            ]
        )
    )

