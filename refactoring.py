from dandy import Map, Bot, BaseIntel, Map
from dandy.recorder import Recorder

Recorder.start_recording('refactoring')

class FrontEndBot(Bot):
    llm_role = 'A Programming Mentor for Front End Developers'

class BackEndBot(Bot):
    llm_role = 'A Programming Mentor for Back End Developers'


class ProgrammingHelpMap(Map):
    mapping_keys_description = 'Programming Problems'
    mapping = {
        'server, python, django, views, models': BackEndBot,
        'css, html, javascript, templates, design': FrontEndBot,
        'anything else related to other C like programing languages': Map(
            mapping_keys_description='Funny Jokes',
            mapping={
                'rust programming language': 'I AM RUSTY!!!'
            }
        )
    }

user_question = 'What does the borrow checker do in this language with the red crab symbol?'
# user_question = 'I am working on a website that and I cannot get the buttons to aling how do I do that?'

programming_help_bots = ProgrammingHelpMap().process(
    user_question,
    max_return_values=1
)

print(programming_help_bots)

# print(programming_help_bots[0]().process(user_question))




# class HatIntel(BaseIntel):
#     color: str
#     size: int
#     style: str
#
# class CharacterIntel(BaseIntel):
#     name: str
#     age: int
#     gender: str
#     height: float
#     weight: float
#     hats: list[HatIntel]
#
# unicorn_character = Bot().process(
#     prompt='Make me a character that would ride a unicorn! give them a selection of hats',
#     intel_class=CharacterIntel,
# )
#
# print(unicorn_character)
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

Recorder.stop_recording('refactoring')

Recorder.to_html_file('refactoring')