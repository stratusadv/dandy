# Workflow

## Bot vs Workflow

While a `Bot/LlmBot` is meant to be single step in a process, a `Workflow` is meant to combine multiple steps into a single process to accomplish something more complex.

## Map vs Workflow

A `Map/LlmMap` is used to make decisions or navigate choices, while a `Workflow` can seem similar, it is a container to help make more complex single processes.

## Creating a Workflow

```python exec="True" source="above" source="material-block" session="workflow"
from dandy.workflow import BaseWorkflow
from dandy.llm import BaseLlmMap, Map, BaseLlmBot, Prompt, LlmConfigOptions
from dandy.intel import BaseIntel


class PlantIntel(BaseIntel):
    name: str
    climate: str
    is_edible: bool | None = None


class ClimateLlmMap(BaseLlmMap):
    config_options = LlmConfigOptions(
        temperature=0.0
    )

    map = Map({
        'very hot and rainy': 'rainforest',
        'very cold and sunny': 'tundra',
        'very hot and sunny': 'desert',
        'very cold and rainy': 'snowfield'
    })


class PlantDescriptionLlmBot(BaseLlmBot):
    @classmethod
    def process(cls, user_prompt: str, climate: str) -> PlantIntel:
        return cls.process_prompt_to_intel(
            prompt=(
                Prompt()
                .heading('Question')
                .text(f'What plant is described in "{user_prompt}"')
                .line_break()
                .heading('Climate')
                .text(climate)
            ),
            intel_class=PlantIntel
        )


class PlantEdibilityLlmBot(BaseLlmBot):
    @classmethod
    def process(cls, plant_intel: PlantIntel) -> PlantIntel:
        return cls.process_prompt_to_intel(
            prompt=Prompt(f'Is {plant_intel.name} edible?'),
            intel_object=plant_intel,
            include_fields={'is_edible'}
        )


class PlantFinderWorkflow(BaseWorkflow):
    @classmethod
    def process(cls, user_prompt: str) -> PlantIntel:
        climates = ClimateLlmMap.process(user_prompt)

        plant_intel = PlantDescriptionLlmBot.process(user_prompt, climates[0])

        return PlantEdibilityLlmBot.process(plant_intel)


plant_intel = PlantFinderWorkflow.process(
    'I am wet from the down pour and its very warm, I see a trees with long yellow fruit bunches.')

print(plant_intel)
```

!!! tip

    Remeber you can use the `@debug_recorder_to_html` on the work flow process to capture the whole process and view it in a browser for easy debugging.