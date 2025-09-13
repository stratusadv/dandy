# Debug Recorder

## Manual Recording

Working with intelligent systems creates a lot of information for simple transactions.

In order to know what is going on we are going to use the `Recorder` class to look inside any `process` methods called.

```python
from dandy import Bot, Recorder
from dandy.recorder import Recorder

Recorder.start_recording(recording_name='tutorial')

canada_capital_intel = Bot().process(prompt='Please tell me just the name only of the city that is the capital of Canada?')

capital_description_intel = Bot().process(prompt=f'Please describe the following city: {canada_capital_intel.content}')

Recorder.stop_recording('tutorial')

Recorder.to_html_file('tutorial')
```

Output: [Debug HTML File](tutorial_recording_output.html){target="_blank"}

!!! note

    The `Recorder` class can debug multiple process sets at the same time by specifying the `debugger_name` argument.

## Decorator Recording

We can accomplish the same as above by using the `@recorder_to_html_file` decorator.

```python
from dandy import Bot, recorder_to_html_file

@recorder_to_html_file(recording_name='tutorial')
def get_canada_capital_description():
    canada_capital_intel = Bot().process(prompt='Please tell me just the name only of the city that is the capital of Canada?')
    return Bot().process(prompt=f'Please describe the following city: {canada_capital_intel.content}')

capital_description_intel = get_canada_capital_description()
```

Output: [Debug HTML File](tutorial_recording_output.html){target="_blank"}

!!! tip

    Having the HTML output file open in a window beside your code editor will help you understand what is going on and drastically speed up the development process.
