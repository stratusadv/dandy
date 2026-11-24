from unittest import TestCase
from unittest.mock import patch

from dandy.domain.message.message import MessageHistory
from dandy.domain.request.request import LlmRequestBody
from dandy.infrastructure.recorder.llm_events import (
    recorder_add_llm_request_event,
    recorder_add_llm_response_event,
)
from dandy.infrastructure.recorder.recorder import Recorder
from dandy.infrastructure.recorder.tool_events import recorder_add_tool_result_event


class TestRecorderEventGating(TestCase):
    def test_request_event_skipped_when_not_recording(self) -> None:
        history = MessageHistory()
        history.add_message(role='system', text='sys')
        history.add_message(role='user', text='hello')
        request_body = LlmRequestBody(model='probe', messages=history)
        request_body.response_format = None

        with patch.object(Recorder, 'add_event') as add_event:
            recorder_add_llm_request_event(request_body, 'probe')

        add_event.assert_not_called()

    def test_request_event_default_schema_does_not_raise_when_idle(self) -> None:
        request_body = LlmRequestBody(model='probe')

        recorder_add_llm_request_event(request_body, 'probe')

    def test_tool_result_event_skipped_when_not_recording(self) -> None:
        with patch.object(Recorder, 'add_event') as add_event:
            recorder_add_tool_result_event('read_file', 'contents', 'probe')

        add_event.assert_not_called()

    def test_response_event_recorded_when_recording(self) -> None:
        Recorder.start_recording('gating_probe')
        try:
            with patch.object(Recorder, 'add_event', wraps=Recorder.add_event) as add_event:
                recorder_add_llm_response_event('hello', 'probe')

            add_event.assert_called_once()
        finally:
            Recorder.stop_recording('gating_probe')
