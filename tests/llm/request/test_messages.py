from unittest import TestCase

from dandy.processor.bot.bot import Bot
from dandy.intel.intel import BaseIntel
from dandy.llm.request.message import MessageHistory

class TestMessages(TestCase):
    def test_message_history(self):
        message_history = MessageHistory()
        message_history.create_message(role='user', text='I was 91 years old a few days ago')
        message_history.create_message(role='system', text='When is your birthday?')
        message_history.create_message(role='user', text='It is my birthday today!')
        message_history.create_message(role='system', text='How old are you?')
        message_history.create_message(role='user', text='I just turned 92')
        message_history.create_message(role='system', text='Wow! That is so old.')
        message_history.create_message(role='user', text='That is ok I am feeling great')

        class BirthdayIntel(BaseIntel):
            past_age: int
            current_age: int

        birthday_intel = Bot().llm.prompt_to_intel(
            prompt='What were my ages in our conversation',
            intel_class=BirthdayIntel,
            message_history=message_history
        )

        self.assertEqual(birthday_intel.past_age, 91)
        self.assertEqual(birthday_intel.current_age, 92)

