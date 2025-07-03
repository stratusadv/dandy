# LLM Bot

## What is a Bot

In Dandy we want to make sure all the things you do have a distinct name to isolate them from your projects code.
Bots should represent a distinct and singular thing you want to do within your project.

## Create a Basic LLM Bot

To create your own bot we are going to use the `BaseLlmBot` class from the `dandy.llm` module.

```python exec="True" source="above" source="material-block" session="llm_bot"
from dandy.llm import BaseLlmBot, Prompt, DefaultLlmIntel

class AssistantBot(BaseLlmBot):
    @classmethod
    def process(cls, user_prompt: Prompt | str) -> DefaultLlmIntel:
        default_intel = cls.process_prompt_to_intel(
            prompt=user_prompt,
            intel_class=DefaultLlmIntel
        )
        
        return default_intel

intel = AssistantBot.process('Can you give me an idea for a book?')

print(intel.text)
```

## Advanced LLM Bot

When you create a bot it uses all the defaults of the `dandy_settings.py` file.

Below is an example of how you can customize bots to make sure they work the way you want.

```python exec="True" source="above" source="material-block" session="llm_bot"
from dandy.intel import BaseIntel
from dandy.llm import BaseLlmBot, Prompt, LlmConfigOptions


class CandyIntel(BaseIntel):
    short_name: str
    long_name: str
    description: str


class CandyDesignBot(BaseLlmBot):
    config = 'LLAMA_3_2_3B'
    config_options = LlmConfigOptions(
        temperature=0.1,
        max_input_tokens=2000,
        max_output_tokens=2000,
        prompt_retry_count=3,
        randomize_seed=True
    )
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

    @classmethod
    def process(cls, user_prompt: Prompt | str, candy_theme: str) -> CandyIntel:
        prompt = (
            Prompt()
            .heading('Request')
            .prompt(user_prompt)
            .line_break()
            .heading('Theme')
            .prompt(candy_theme)
        )

        return cls.process_prompt_to_intel(
            prompt=prompt,
        )


candy_intel = CandyDesignBot.process(
    user_prompt='Strawberries and Cookie Dough',
    candy_theme='Medieval Times'
)

print(candy_intel)
```

