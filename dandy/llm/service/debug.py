from pydantic import ValidationError

from dandy.core.utils import pydantic_validation_error_to_str
from dandy.debug.debug import DebugRecorder
from dandy.intel import BaseIntel
from dandy.llm.service.events import LlmServiceRequestEvent, LlmServiceResponseEvent, LlmServiceSuccessEvent, \
    LlmServiceFailureEvent, LlmServiceRetryEvent
from dandy.llm.service.request.request import BaseRequestBody
from dandy.llm.tokens.utils import get_estimated_token_count_for_string


def debug_record_llm_validation_failure(error: ValidationError, event_id: str):
    if DebugRecorder.is_recording:
        DebugRecorder.add_event(LlmServiceFailureEvent(
            description=pydantic_validation_error_to_str(error),
            id=event_id
        ))


def debug_record_llm_retry(description: str, event_id: str, remaining_attempts: int = None):
    if DebugRecorder.is_recording:
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
            estimated_tokens=get_estimated_token_count_for_string(message_content),
            id=event_id
        ))

def debug_record_llm_success(description: str, event_id: str, intel: BaseIntel = None):
    if DebugRecorder.is_recording:
        intel_json = None

        if intel:
            intel_json = intel.model_dump_json(indent=4)

        DebugRecorder.add_event(LlmServiceSuccessEvent(
            description=f'{description}\n\n{intel.__class__.__name__}: {intel_json}' if intel_json else description,
            id=event_id
        ))

