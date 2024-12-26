from pydantic import BaseModel, ValidationError

from dandy.core.utils import pydantic_validation_error_to_str
from dandy.debug.debug import DebugRecorder
from dandy.llm.request.request import BaseRequestBody
from dandy.llm.service.events import LlmServiceRequestEvent, LlmServiceResponseEvent, LlmServiceSuccessEvent, \
    LlmServiceFailureEvent, LlmServiceRetryEvent
from dandy.llm.utils import str_to_token_count


def debug_record_llm_validation_failure(error: ValidationError, event_id: str):
    if DebugRecorder.is_recording:
        DebugRecorder.add_event(LlmServiceFailureEvent(
            description=pydantic_validation_error_to_str(error),
            id=event_id
        ))


def debug_record_llm_retry(description: str, event_id: str, remaining_attempts: int = None):
    DebugRecorder.add_event(LlmServiceRetryEvent(
        description=f'{description}\nRemaining Attempts: {remaining_attempts}' if remaining_attempts is not None else description,
        id=event_id
    ))


def debug_record_llm_request(request_body: BaseRequestBody, event_id: str):
    if DebugRecorder.is_recording:
        DebugRecorder.add_event(LlmServiceRequestEvent(
            request=request_body.model_dump(),
            temperature=request_body.get_temperature(),
            estimated_tokens=request_body.messages_estimated_tokens,
            id=event_id
        ))


def debug_record_llm_response(message_content: str, event_id: str):
    if DebugRecorder.is_recording:
        DebugRecorder.add_event(LlmServiceResponseEvent(
            response=message_content,
            estimated_tokens=str_to_token_count(message_content),
            id=event_id
        ))

def debug_record_llm_success(description: str, event_id: str, model: BaseModel = None):
    if DebugRecorder.is_recording:
        model_json = None

        if model:
            model_json = model.model_dump_json(indent=4)

        DebugRecorder.add_event(LlmServiceSuccessEvent(
            description=f'{description}\n\n{model.__class__.__name__}: {model_json}' if model_json else description,
            id=event_id
        ))

