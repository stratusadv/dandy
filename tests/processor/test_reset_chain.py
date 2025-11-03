from unittest import TestCase, mock

from dandy.processor.agent.agent import Agent
from dandy.processor.decoder.decoder import Decoder
from dandy.processor.agent.service import AgentService
from dandy.processor.bot.bot import Bot
from dandy.core.service.mixin import BaseServiceMixin
from dandy.llm.service import LlmService
from dandy.http.service import HttpService
from dandy.intel.service import IntelService
from dandy.processor.bot.service import BotService
from dandy.processor.decoder.service import DecoderService
from dandy.vision.service import VisionService


class TestProcessorResetChain(TestCase):
    def setUp(self):
        self.patcher_base = mock.patch.object(
            BaseServiceMixin, 'reset_services', new=lambda self: None
        )
        self.patcher_bot = mock.patch.object(BotService, 'reset_service')
        self.patcher_agent = mock.patch.object(AgentService, 'reset_service')
        self.patcher_decoder = mock.patch.object(DecoderService, 'reset_service')
        self.patcher_llm = mock.patch.object(LlmService, 'reset_service')
        self.patcher_http = mock.patch.object(HttpService, 'reset_service')
        self.patcher_intel = mock.patch.object(IntelService, 'reset_service')
        self.patcher_vision = mock.patch.object(VisionService, 'reset_service')

        self.mock_bot_reset = self.patcher_bot.start()
        self.mock_agent_reset = self.patcher_agent.start()
        self.mock_decoder_reset = self.patcher_decoder.start()
        self.mock_llm_reset = self.patcher_llm.start()
        self.mock_http_reset = self.patcher_http.start()
        self.mock_intel_reset = self.patcher_intel.start()
        self.mock_vision_reset = self.patcher_vision.start()
        self.patcher_base.start()

    def tearDown(self):
        self.patcher_base.stop()
        self.patcher_bot.stop()
        self.patcher_agent.stop()
        self.patcher_decoder.stop()
        self.patcher_llm.stop()
        self.patcher_http.stop()
        self.patcher_intel.stop()
        self.patcher_vision.stop()

    def test_agent_reset_services(self):
        agent = Agent()
        agent.reset_services()

        self.mock_agent_reset.assert_called_once()
        self.mock_llm_reset.assert_called_once()
        self.mock_http_reset.assert_called_once()
        self.mock_intel_reset.assert_called_once()

        self.mock_bot_reset.assert_not_called()
        self.mock_decoder_reset.assert_not_called()
        self.mock_vision_reset.assert_not_called()

    def test_bot_reset_services(self):
        bot = Bot()
        bot.reset_services()

        self.mock_bot_reset.assert_called_once()
        self.mock_llm_reset.assert_called_once()
        self.mock_http_reset.assert_called_once()
        self.mock_intel_reset.assert_called_once()

        self.mock_agent_reset.assert_not_called()
        self.mock_decoder_reset.assert_not_called()
        self.mock_vision_reset.assert_not_called()

    def test_decoder_reset_services(self):
        decoder = Decoder(
            mapping_keys_description='Nothing',
            mapping={}
        )
        decoder.reset_services()

        self.mock_decoder_reset.assert_called_once()
        self.mock_llm_reset.assert_called_once()

        self.mock_agent_reset.assert_not_called()
        self.mock_bot_reset.assert_not_called()
        self.mock_http_reset.assert_not_called()
        self.mock_intel_reset.assert_not_called()
        self.mock_vision_reset.assert_not_called()
