# Setting Up Your Project

## Installation

Just like most python packages you can easily install Dandy using pip.

``` bash
pip install dandy
```

!!! info

    The Dandy package will also install 
    [`httpx`](https://www.python-httpx.org/), 
    [`pydantic`](https://docs.pydantic.dev/latest/) and
    [`python-dotenv`](https://github.com/theskumar/python-dotenv) packages.

## Creating a Settings File

You can create a `dandy_settings.py` file in the root of your project with the following contents.

```python title="dandy_settings.py"
import os
from pathlib import Path

ALLOW_RECORDING_TO_FILE = True

BASE_PATH = Path.resolve(Path(__file__)).parent

LLM_CONFIGS = {
    'DEFAULT': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_HOST"),
        'PORT': int(os.getenv("OLLAMA_PORT", 11434)),
        'API_KEY': os.getenv("OLLAMA_API_KEY"),
        'MODEL': 'llama3.1:8b-instruct-q4_K_M',
    },
    'LLAMA_3_2_3B': {
        'MODEL': 'llama3.2:3b-instruct-q4_K_M',
    },
    'GPT_4o': {
        'TYPE': 'openai',
        'HOST': os.getenv("OPENAI_HOST"),
        'PORT': int(os.getenv("OPENAI_PORT", 443)),
        'API_KEY': os.getenv("OPENAI_API_KEY"),
        'MODEL': 'gpt-4o',
    },
}
```

This configuration allows us to use both Ollama and OpenAI as our LLM services.

The `DEFAULT` in the `LLM_CONFIGS` will be used when no other config is specified for any llm actions.

!!! tip

    Once the `DEFAULT` config is specified, the `TYPE`, `HOST`, `PORT` AND `API_KEY` from the `DEFAULT` config will flow to the other configs if they are not specificed.

## Environment Variables

The `DANDY_SETTINGS_MODULE` environment variable can be used to specify the settings module to be used.

```bash
export DANDY_SETTINGS_MODULE=dandy_settings
```

!!! note

    If the `DANDY_SETTINGS_MODULE` environment variable is not set, the system will default to look for a `dandy_settings.py` file in the current working directory or sys.path.