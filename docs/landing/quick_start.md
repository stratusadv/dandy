# Quick Start Dandy!

## Installation

Just like most python packages you can easily install Dandy using pip.

``` bash
pip install dandy
```

## Create a Settings File

You can create a `dandy_settings.py` file in the root of your project with the following contents.  

```python title="dandy_settings.py"
import os
from pathlib import Path

ALLOW_DEBUG_RECORDING = True

BASE_PATH = Path.resolve(Path(__file__)).parent

LLM_CONFIGS = {
    'DEFAULT': {
        'TYPE': 'openai',
        'HOST': 'https://api.openai.com',
        'PORT': 443,
        'API_KEY': os.getenv('OPENAI_API_KEY'),
        'MODEL': 'gpt-4o-mini',
    }
}

# or

LLM_CONFIGS = {
    'DEFAULT': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_HOST"),
        'PORT': int(os.getenv("OLLAMA_PORT", 11434)),
        'API_KEY': os.getenv("OLLAMA_API_KEY"), 
        'MODEL': 'llama3.1:8b',
    },}
```

## Simple LLM Interaction

Once you have Dandy setup and configured you can easily get started with a simple LLM interaction.

```python exec="True" source="above" source="material-block"

from dandy import Bot

response = Bot().process('What is the capital of Canada?')

print(response.text)

```

## Start Learning

Wow, that was easy ... we are only beginning to dive into the power of Dandy.

If you have already got the [setup](../tutorials/setup.md) process complete you can skip right to the [intel tutorial](../tutorials/intel.md).