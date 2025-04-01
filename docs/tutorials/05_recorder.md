# Debug Recorder

## Manual Recording

Working with intelligent systems creates a lot of information for simple transactions.

In order to know what is going on we are going to use the `DebugRecorder` class to look inside any `process` methods called.

```python
from dandy.llm import LlmBot
from dandy.debug import DebugRecorder

DebugRecorder.start_recording(debugger_name='tutorial')

canada_capital_intel = LlmBot.process(prompt='Please tell me just the name only of the city that is the capital of Canada?')

capital_description_intel = LlmBot.process(prompt=f'Please describe the following city: {canada_capital_intel.text}')

DebugRecorder.stop_recording('tutorial')

DebugRecorder.to_html_file('tutorial')
```

Output: [Debug HTML File](tutorial_debug_output.html){target="_blank"}

!!! note

    The `DebugRecorder` class can debug multiple process sets at the same time by specifying the `debugger_name` argument.

## Decorator Recording

We can accomplish the same as above by using the `@debug_recorder_to_html` decorator.

```python
from dandy.llm import LlmBot
from dandy.debug import debug_recorder_to_html

@debug_recorder_to_html(debugger_name='tutorial')
def get_canada_capital_description():
    canada_capital_intel = LlmBot.process(prompt='Please tell me just the name only of the city that is the capital of Canada?')
    return LlmBot.process(prompt=f'Please describe the following city: {canada_capital_intel.text}')

capital_description_intel = get_canada_capital_description()
```

Output: [Debug HTML File](tutorial_debug_output.html){target="_blank"}

!!! tip

    Having the HTML output file open in a window beside your code editor will help you understand what is going on and drastically speed up the development process.
