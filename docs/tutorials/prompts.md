# Prompts

## Prompt vs String

We recommend using our `Prompt` class to create prompts as it provides a lot of extra features and capabilities over a simple string.

The main advantage to this is that as feature and formatting improves over time for AI models, you can ensure that your project is using consistent formatting.

## Creating a Prompt

Creating a new prompt is simple and can be done multiple ways each have their own pros and cons.

### Structured Style Prompt

this method is the best for creating prompts that are complex and can be statically typed.

```python exec="True" source="above" source="material-block" result="markdown" session="prompt"
from dandy.llm.prompt import Prompt

prompt = (
    Prompt()
    .title('Car Generator')
    .line_break()
    .heading('Instructions')
    .text('I would like you to create me a new type of car.')
    .line_break()
    .heading('Rules')
    .list([
        'The car should be fast',
        'The car should be safe',
        'The car should be fun to drive',
    ])
)
print(prompt.to_str())
```

### Dynamic Style Prompt

This method is the best for creating prompts that are complex or need to have things injected into them.

```python exec="True" source="above" source="material-block" result="markdown" session="prompt"
from dandy.llm.prompt import Prompt

CAR_RULES = [
    'The car should be fast',
    'The car should be safe',    
    'The car should be fun to drive',
]

prompt = Prompt()
prompt.title('Car Generator')
prompt.line_break()

prompt.heading('Instructions')
prompt.text('I would like you to create me a new type of car.')
prompt.line_break()

prompt.heading('Rules')
prompt.list(CAR_RULES)

print(prompt.to_str())
```

### String Style Prompt

This method is the best for creating prompts that are simple and do not need structured formatting.

```python exec="True" source="above" source="material-block" result="markdown" session="prompt"
from dandy.llm.prompt import Prompt

prompt = Prompt("""
# Car Generator

## Instructions
I would like you to create me a new type of car.

## Rules
- The car should be fast
- The car should be safe
- The car should be fun to drive
""")

print(prompt.to_str())
```

## Prompt Formatting

There is lots of different types of formatting that can be used to create prompts.

```python exec="True" source="above" source="material-block" result="markdown" session="prompt"
from dandy.llm.prompt import Prompt
from dandy.intel import BaseIntel

class PersonIntel(BaseIntel):
    name: str
    age: int

person_intel = PersonIntel(name='John', age=30)

another_prompt = (
    Prompt()
    .text('Hello from another prompt')
)

new_prompt = (
    Prompt()
    .dict(dictionary={'key': 'value'})
    .divider()
    .array(items=['item1', 'item2'])
    .array_random_order(items=['item1', 'item2'])
    .file(file_path='docs/tutorials/prompt_test_document.md')
    .heading(heading='Heading Followed by a line break')
    .line_break()
    .list(items=['item1 after a line break', 'item2'])
    .intel(intel=person_intel)
    .intel_schema(intel_class=PersonIntel)
    .module_source(module_name='dandy.llm.bot.llm_bot')
    .ordered_list(items=['item1', 'item2'])
    .prompt(prompt=another_prompt)
    .random_choice(choices=['choice1', 'choice2'])
    .sub_heading(sub_heading='Sub Heading')
    .text('Hello World')
    .title(title='Title')
    .unordered_list(items=['item1', 'item2'])
    .unordered_random_list(items=['item1', 'item2'])
)

print(new_prompt.to_str())
```

!!! tip

    Check out the [Prompt](../api/llm/prompt/prompt.md) and [Snippets](../api/llm/prompt/snippet.md) API documentation for more information on all the possibilities.

## Advanced Prompts

Let's make a function that returns a dynamically constructed prompt based on the function arguments.

```python exec="True" source="above" source="material-block" result="markdown" session="prompt"
from dandy.llm.prompt import Prompt

def generate_prompt(name: str, age: int) -> Prompt:
    prompt = Prompt()

    prompt.text(f'Hello {name} you are {age} years old.')

    return prompt

prompt = generate_prompt('John', 30)

print(prompt.to_str())
```