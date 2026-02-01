from unittest import TestCase, mock

from dandy.file.service import FileService

from dandy.bot.bot import Bot
from dandy.core.service.mixin import BaseServiceMixin
from dandy.llm.service import LlmService
from dandy.http.service import HttpService
from dandy.intel.service import IntelService
from dandy.llm.decoder.service import DecoderService


class TestProcessorResetChain(TestCase):
    def test_bot_reset_services(self):
        bot = Bot()
        # Mock the service instances to avoid real service initialization
        bot._LlmService_instance = mock.Mock()
        bot._HttpService_instance = mock.Mock()
        bot._IntelService_instance = mock.Mock()
        bot._DecoderService_instance = mock.Mock()
        bot._FileService_instance = mock.Mock()

        bot.reset_services()

        bot._LlmService_instance.reset_service.assert_called_once()
        bot._HttpService_instance.reset_service.assert_called_once()
        bot._IntelService_instance.reset_service.assert_called_once()
        bot._FileService_instance.reset_service.assert_called_once()

        bot._DecoderService_instance.reset_service.assert_not_called()
