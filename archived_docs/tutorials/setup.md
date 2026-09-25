# Setting Up Your Project

## Installation

Just like most python packages you can easily install Dandy using pip.

``` bash
pip install dandy
```

!!! info

    The Dandy package will also install
    [`blessed`](https://blessed.readthedocs.io/),
    [`requests`](https://requests.readthedocs.io/),
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
        'HOST': os.getenv('OPENAI_HOST', 'https://api.openai.com'),
        'PORT': int(os.getenv('OPENAI_PORT', 443)),
        'API_KEY': os.getenv('OPENAI_API_KEY'),
        'MODEL': 'gpt-4o-mini',
    },
    'GPT_4o': {
        'MODEL': 'gpt-4o',
    },
}
```

This configuration sets up OpenAI as the LLM service with multiple model options.

The `DEFAULT` in the `LLM_CONFIGS` will be used when no other config is specified for any llm actions.

!!! tip

    Once the `DEFAULT` config is specified, the `HOST`, `PORT` AND `API_KEY` from the `DEFAULT` config will flow to the other configs if they are not specified.

## Environment Variables

The `DANDY_SETTINGS_MODULE` environment variable can be used to specify the settings module to be used.

```bash
export DANDY_SETTINGS_MODULE=dandy_settings
```

!!! note

    If the `DANDY_SETTINGS_MODULE` environment variable is not set, the system will default to look for a `dandy_settings.py` file in the current working directory or sys.path.

## More Settings

There are more settings you can configure in your project see below for more information.

```py title="dandy/default_settings.py"
--8<-- "dandy/default_settings.py"
```


