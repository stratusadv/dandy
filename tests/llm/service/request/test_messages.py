from unittest import TestCase

from dandy.intel import BaseIntel
from dandy.llm import MessageHistory, LlmBot

class TestMessages(TestCase):
    def test_message_history(self):
        message_history = MessageHistory()
        message_history.add_message('user', 'I was 91 years old a few days ago')
        message_history.add_message('system', 'When is your birthday?')
        message_history.add_message('user', 'It is my birthday today!')
        message_history.add_message('system', 'How old are you?')
        message_history.add_message('user', 'I just turned 92')
        message_history.add_message('system', 'Wow! That is so old.')
        message_history.add_message('user', 'That is ok I am feeling great')

        class BirthdayIntel(BaseIntel):
            past_age: int
            current_age: int

        birthday_intel = LlmBot.process(
            prompt='What were my ages in our conversation',
            intel_class=BirthdayIntel,
            message_history=message_history
        )

        self.assertEqual(birthday_intel.past_age, 91)
        self.assertEqual(birthday_intel.current_age, 92)

