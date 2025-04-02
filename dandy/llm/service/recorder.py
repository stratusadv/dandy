import json

from pydantic import ValidationError

from dandy.core.utils import pydantic_validation_error_to_str
from dandy.recorder.recorder import Recorder
from dandy.intel import BaseIntel
from dandy.llm.service.request.request import BaseRequestBody
from dandy.llm.tokens.utils import get_estimated_token_count_for_string
from dandy.recorder.events import Event, EventItem, EventType

_EVENT_OBJECT_NAME = 'LLM Service'


def recorder_add_llm_validation_failure_event(
        error: ValidationError,
        event_id: str
):
    Recorder.add_event(
        Event(
            id=event_id,
            object_name=_EVENT_OBJECT_NAME,
            callable_name='Validation',
            type=EventType.FAILURE,
            items=[
                EventItem(
                    key='Error',
                    value=pydantic_validation_error_to_str(error)
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
            items=[
                EventItem(
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
        items=[
            EventItem(
                key='Model',
                value=request_body.model
            ),
            EventItem(
                key='Temperature',
                value=request_body.get_temperature()
            ),
            EventItem(
                key='Estimated Tokens',
                value=request_body.messages_estimated_tokens
            ),
            EventItem(
                key='JSON Schema',
                value=json.dumps(json_schema, indent=4),
                is_dropdown=True,
            )
        ]
    )

    for message in request_body.messages:
        llm_request_event.add_item(EventItem(
            key=message.role,
            value=message.content,
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
            items=[
                EventItem(
                    key='Estimated Tokens',
                    value=get_estimated_token_count_for_string(message_content),
                ),
                EventItem(
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
            items=[
                EventItem(
                    key='Status',
                    value=description,
                ),
                EventItem(
                    key=intel.__class__.__name__ if intel_json else 'Result',
                    value=intel_json if intel_json else 'None',
                    is_card=True
                ),
            ]
        )
    )

