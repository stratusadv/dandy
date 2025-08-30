from dandy import Map, Bot, BaseIntel
from dandy.recorder import Recorder

Recorder.start_recording('refactoring')

class DefaultIntel(BaseIntel):
    text: str

class BearBot(Bot):
    def process(self, user_input: str) -> DefaultIntel:
        return self.llm.prompt_to_intel(
            prompt=user_input,
            intel_class=DefaultIntel,
        )


# print(BearBot().process('Tell me about flying bears').text)
# print(BearBot().process('What are cartoon bears?').text)

new_map = Map(
    mapping_keys_description='Types of Tacos',
    mapping={
        'Beef': 1,
        'Chicken': 2,
        'Pork': 3,
        'Vegetarian': {
            'Onions': 4,
            'Spinach': 5,
            'Tomatoes': 6,
        }
    }
)

answers = new_map.process('I really do not like eating animals, and I enjoy acidic food')

print(answers)

Recorder.stop_recording('refactoring')

Recorder.to_html_file('refactoring')