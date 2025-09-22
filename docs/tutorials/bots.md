# Bot

## What is a Bot

In Dandy, we want to make sure all the things you do have a distinct name to isolate them from your project's code.
Bots should represent a singular action you want to do within your project.

## Create a Basic Bot

To create your own bot, we are going to use the `Bot` class from the `dandy.llm` module.

```python exec="True" source="above" source="material-block" session="bot"
from dandy import Bot, Prompt

class AssistantBot(Bot):
    def process(self, user_prompt: Prompt | str):
        default_intel = self.llm.prompt_to_intel(
            prompt=user_prompt,
        )
        
        return default_intel

intel = AssistantBot().process('Can you give me an idea for a book?')

print(intel.content)
```

## Advanced Bot

When you create a bot it uses all the defaults of the `dandy_settings.py` file.

Below is an example of how you can customize bots to make sure they work the way you want.

```python exec="True" source="above" source="material-block" session="bot"
from dandy import BaseIntel, Bot, Prompt


class CandyIntel(BaseIntel):
    short_name: str
    long_name: str
    description: str


class CandyDesignBot(Bot):
    llm_config = 'LLAMA_3_2_3B'
    # llm_config_options = LlmConfigOptions(
    #     temperature=0.1,
    #     max_input_tokens=2000,
    #     max_output_tokens=2000,
    #     prompt_retry_count=3,
    #     randomize_seed=True
    # )
    instructions_prompt = (
        Prompt()
        .text('You are a candy design bot and will be given a request to make a new type of candy.')
        .line_break()
        .heading('Rules')
        .list([
            'Make sure you response is sugar based not chocolate based.',
            'Do not include any chocolate based words or phrases in the response.',
            'Incorporate the theme of the request into the response.',
        ])
    )
    intel_class = CandyIntel

    def process(self, user_prompt: Prompt | str, candy_theme: str) -> CandyIntel:
        prompt = (
            Prompt()
            .heading('Request')
            .prompt(user_prompt)
            .line_break()
            .heading('Theme')
            .prompt(candy_theme)
        )

        return self.llm.prompt_to_intel(
            prompt=prompt,
        )


candy_intel = CandyDesignBot().process(
    user_prompt='Strawberries and Cookie Dough',
    candy_theme='Medieval Times'
)

print(candy_intel)
```