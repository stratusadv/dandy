from dandy import Bot, BaseIntel
from dandy.recorder import Recorder

Recorder.start_recording("refactoring")


class HatIntel(BaseIntel):
    color: str
    size: int
    style: str


class CharacterIntel(BaseIntel):
    name: str
    age: int
    gender: str
    height: float
    weight: float
    hats: list[HatIntel]


class UnicornBot(Bot):
    llm_role: str = "Character Makers"
    llm_task: str = "Make amazing characters!"
    llm_guidelines: str = "Use fun names"

unicorn_bot = UnicornBot()

unicorn_character = unicorn_bot.process(
    prompt="Make me a character that would ride a unicorn! give them a selection of hats",
    intel_class=CharacterIntel,
)

print(unicorn_character)
#
# for hat in unicorn_character.hats:
#     print(hat.style)

# print(unicorn_character.name)

# class DefaultIntel(BaseIntel):
#     text: str
#
# class BearBot(Bot):
#     def process(self, user_input: str) -> DefaultIntel:
#         return self.llm.prompt_to_intel(
#             prompt=user_input,
#             intel_class=DefaultIntel,
#         )
#
#
# # print(BearBot().process('Tell me about flying bears').text)
# # print(BearBot().process('What are cartoon bears?').text)
#
# new_map = Map(
#     mapping_keys_description='Types of Tacos',
#     mapping={
#         'Beef': 1,
#         'Chicken': 2,
#         'Pork': 3,
#         'Vegetarian': {
#             'Onions': 4,
#             'Spinach': 5,
#             'Tomatoes': 6,
#         }
#     }
# )
#
# answers = new_map.process('I really do not like eating animals, and I enjoy acidic food')
#
# print(answers)

Recorder.stop_recording("refactoring")

Recorder.to_html_file('refactoring')
