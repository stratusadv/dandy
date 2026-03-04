# GitHub Copilot Code Review Instructions

## Project Context

Dandy is a Python Artificial Intelligence Framework that simplifies the development of AI software. It provides abstractions for interacting with LLMs, managing state, processing data, and orchestrating AI workflows.

### Key Concepts

- **Bot**: A singular AI-powered action or service that processes prompts and returns Intel
- **Prompt**: A structured object for building LLM prompts with formatting capabilities
- **Intel**: Pydantic models that represent structured data returned from LLMs
- **Decoder**: Selects from dictionary mappings based on LLM responses
- **Recorder**: Captures and logs all LLM interactions for debugging and analysis
- **Cache**: Memory and SQLite-based caching for repeated operations

> **Important**: The Agent module was removed in v2.0.0. For complex workflows, compose multiple Bot instances or implement custom logic in `process()` methods.

## Coding Standards

### Code Style

- **Quote style**: Single quotes (configured in `ruff.toml`)
- **Line length**: 88 characters max
- **Imports**: Follow this order: standard library → third-party → local (dandy.*)
- **Type hints**: Always use type hints for function signatures
- **Imports**: Use absolute imports (e.g., `from dandy.bot.bot import Bot`)
- **Verbose**: Always use verbose names (e.g., `sub_command` not `subcmd`)

### Naming Conventions

- **Classes**: PascalCase (e.g., `Bot`, `Prompt`, `BaseIntel`)
- **Functions/Methods**: snake_case (e.g., `process`, `get_llm_config`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `ALLOW_RECORDING_TO_FILE`)
- **Files**: snake_case (e.g., `bot.py`, `prompt.py`)
- **Directories**: snake_case (e.g., `llm/`, `intel/`, `recorder/`)

## Core Patterns

### Bot Pattern

All bots should extend from `dandy.Bot` and implement a `process()` method:

```python
from dandy import Bot, Prompt, BaseIntel

class MyBot(Bot):
    """Custom bot for specific AI tasks."""
    
    # Optional: Override defaults
    llm_config = 'DEFAULT'
    role = 'Assistant'
    task = 'Provide helpful responses'
    
    def process(self, user_input: Prompt | str) -> BaseIntel:
        """Process the user's prompt and return Intel."""
        return self.llm.prompt_to_intel(prompt=user_input)
```

**Key points:**
- Use `__post_init__()` for custom initialization (call `super().__post_init__()`)
- The `process()` method is automatically wrapped with recorder events
- Support both `Prompt` objects and plain strings as input
- Return `BaseIntel` or a custom Intel subclass

### Prompt Pattern

Prefer the `Prompt` class over raw strings for building prompts:

```python
from dandy import Prompt

# Structured style (recommended for complex prompts)
prompt = (
    Prompt()
    .title('Task Generator')
    .heading('Instructions')
    .text('Create a list of tasks')
    .heading('Rules')
    .list([
        'Tasks should be actionable',
        'Keep tasks concise',
    ])
)

# Dynamic style (for programmatic construction)
prompt = Prompt()
prompt.title('Task Generator')
prompt.heading('Instructions')
prompt.text('Create a list of tasks')

# String style (for simple prompts)
prompt = Prompt("""
# Task Generator

## Instructions
Create a list of tasks
""")
```

**Available methods:**
- `.text(text)` - Add plain text
- `.heading(text)` - Add a heading
- `.title(text)` - Add a title
- `.list(items)` - Add a bulleted list
- `.dict(dictionary)` - Add a dictionary
- `.file(path)` - Include a file's contents
- `.directory_list(path)` - Include directory structure
- `.divider()` - Add a visual divider
- `.line_break()` - Add a line break

### Intel Pattern

All structured data should be modeled as Intel (Pydantic models):

```python
from dandy import BaseIntel

class PersonIntel(BaseIntel):
    """Represents a person's data."""
    first_name: str
    last_name: str
    age: int
    email: str | None = None  # Optional field

class ComplexIntel(BaseIntel):
    """Intel can contain nested Intel objects."""
    person: PersonIntel
    tags: list[str]
    metadata: dict[str, Any]
```

**Key features:**
- Use `model_inc_ex_class_copy()` to create modified versions with filtered fields
- Use `model_to_kwargs()` to convert to a dictionary
- Use `create_from_file()` to load from JSON files
- Support Pydantic features: validation, serialization, schema generation

**Field filtering example:**
```python
# Include only specific fields
PersonSubset = PersonIntel.model_inc_ex_class_copy(include={'first_name', 'last_name'})

# Exclude specific fields
PersonNoEmail = PersonIntel.model_inc_ex_class_copy(exclude={'email'})

# Deep filtering (for nested Intel)
PersonSimple = PersonIntel.model_inc_ex_class_copy(
    include={
        'first_name': True,
        'last_name': True,
        'metadata': {'tags': True}
    }
)
```

### Decoder Pattern

Use decoders to select from dictionary mappings based on LLM responses:

```python
from dandy import Bot

class MyBot(Bot):
    def process(self, user_input: str) -> dict:
        """Select from choices using decoder."""
        choices = {
            'option_a': 'Option A Description',
            'option_b': 'Option B Description',
            'option_c': 'Option C Description',
        }
        
        # Use the decoder via the LLM service
        values = self.llm.decoder.prompt_to_values(
            prompt=user_input,
            keys_description='Choose a processing option',
            keys_values=choices,
            max_return_values=1
        )
        
        # Access selected values
        return values
```

**Key points:**
- All decoder keys must be strings
- Returns `DecoderValuesIntel` with selected values
- Automatically retries on errors (no keys, too many keys)
- Convert to enum with `.as_enum()` for type safety

### Service & Mixin Pattern

Dandy uses a mixin-based architecture for service integration:

```python
from dandy import Bot
from dandy.file.mixin import FileServiceMixin
from dandy.http.mixin import HttpServiceMixin

class AdvancedBot(Bot):
    """Bot with multiple services enabled."""
    
    def process(self, url: str) -> str:
        """Use HTTP service to fetch data."""
        response = self.http.get(url)
        return response.json_data
    
    def read_file(self, path: str) -> str:
        """Use file service to read a file."""
        return self.file.read(path)
```

**Available mixins:**
- `FileServiceMixin` - File operations (read, write, exists, etc.)
- `HttpServiceMixin` - HTTP requests (GET, POST, etc.)
- `IntelServiceMixin` - Intel processing helpers
- `LlmServiceMixin` - LLM operations (prompt_to_intel, prompt_to_decoder)

## Testing Standards

### Test Structure

Tests use Python's unittest framework:

```
tests/
├── bot/
│   ├── test_bot.py
│   └── intelligence/        # Test helpers (bots, intel)
├── llm/
│   ├── test_service.py
│   ├── decoder/
│   │   └── test_decoder.py
│   └── prompt/
│       └── test_prompt.py
├── intel/
│   └── test_base_intel.py
├── recorder/
│   └── test_recorder.py
└── example_project/         # Integration tests
```

### Test Patterns

**Basic test structure:**
```python
from unittest import TestCase
from dandy import Bot, BaseIntel

class TestMyBot(TestCase):
    def test_bot_basic_functionality(self):
        bot = Bot()
        result = bot.process('Test prompt')
        self.assertIsNotNone(result)
```

**Testing with custom Intel:**
```python
from tests.bot.intelligence.bots import MoneyBagBot
from tests.bot.intelligence.intel import MoneyBagIntel

class TestMoneyBagBot(TestCase):
    def test_bot_intel_class_include(self):
        bot = MoneyBagBot()
        result = bot.process(
            user_input='I have 14 coins',
            intel_class=MoneyBagIntel,
            include={'coins'},
        )
        self.assertEqual(result.coins, 14)
```

**Mocking LLM responses:**
```python
from unittest import mock
from dandy import Bot
from dandy.http.intelligence.intel import HttpResponseIntel

@mock.patch('dandy.http.connector.HttpConnector.request_to_response')
def test_with_mocked_response(self, mock_request):
    mock_request.return_value = HttpResponseIntel(
        status_code=200,
        json_data={
            'choices': [{
                'message': {
                    'content': '{"keys": ["1", "2"]}',
                }
            }]
        },
    )
    
    bot = Bot()
    result = bot.process('Test')
    # Assert on result
```

**Testing with multiple LLM configs:**
```python
from tests.llm.decorators import run_llm_configs

class TestMyBot(TestCase):
    @run_llm_configs()
    def test_with_all_configs(self, llm_config: str):
        bot = MyBot(llm_config=llm_config)
        result = bot.process('Test')
        self.assertIsNotNone(result)
```

**Recorder testing:**
```python
from dandy import Recorder

def test_with_recording(self):
    Recorder.start_recording('test_name')
    
    bot = Bot()
    bot.process('Test prompt')
    
    Recorder.stop_recording('test_name')
    Recorder.to_html_file('test_name')  # Generate debug report
```

### Test Helpers

Create test intelligence in `tests/{module}/intelligence/`:

```python
# tests/bot/intelligence/bots.py
from dandy import Bot, BaseIntel

class TestBot(Bot):
    def process(self, user_input: str) -> BaseIntel:
        return self.llm.prompt_to_intel(prompt=user_input)

# tests/bot/intelligence/intel.py
from dandy import BaseIntel

class TestIntel(BaseIntel):
    field1: str
    field2: int
```

## Error Handling

### Exception Hierarchy

```python
# Core exceptions
DandyError                # Base exception
├── DandyCriticalError    # Cannot recover, should fail fast
└── DandyRecoverableError # Can retry or recover

# Intel-specific
IntelCriticalError      # Intel operations

# Decoder-specific
DecoderCriticalError             # Invalid decoder usage
DecoderRecoverableError          # Retryable decoder errors
DecoderNoKeysRecoverableError    # No keys returned (retry)
DecoderToManyKeysRecoverableError # Too many keys (retry)
```

### Error Handling Patterns

```python
from dandy import Bot
from dandy.core.exceptions import DandyRecoverableError

class MyBot(Bot):
    def process(self, user_input: str) -> str:
        try:
            result = self.llm.prompt_to_intel(prompt=user_input)
            return result.text
        except DandyRecoverableError as e:
            # Handle recoverable error
            self.logger.warning(f'Recoverable error: {e}')
            return self.fallback_response()
        except Exception as e:
            # Critical error - re-raise
            raise
```

**Best practices:**
- Catch `DandyRecoverableError` for retryable operations
- Catch `DandyCriticalError` for programming errors (usually shouldn't catch)
- Log recoverable errors with context
- Provide fallback behavior when possible

## Configuration

### Settings File

Create `dandy_settings.py` in project root:

```python
import os
from pathlib import Path

# Required
BASE_PATH = Path.resolve(Path(__file__)).parent

# Optional: Enable file recording
ALLOW_RECORDING_TO_FILE = True

# LLM Configuration
LLM_CONFIGS = {
    'DEFAULT': {
        'HOST': os.getenv('OPENAI_HOST', 'https://api.openai.com'),
        'PORT': int(os.getenv('OPENAI_PORT', 443)),
        'API_KEY': os.getenv('OPENAI_API_KEY'),
        'MODEL': 'gpt-4o-mini',
        'OPTIONS': {
            'temperature': 0.7,
            'max_completion_tokens': None,
        }
    },
    'GPT_4o': {
        'MODEL': 'gpt-4o',
    },
    'THINKING': {
        'MODEL': 'gpt-4o',
        'OPTIONS': {
            'thinking': {'type': 'enabled'},
            'max_completion_tokens': 16384,
        }
    },
}
```

**Key settings:**
- `BASE_PATH`: Project root directory (required)
- `ALLOW_RECORDING_TO_FILE`: Enable file-based recording
- `DANDY_DIRECTORY`: Directory for Dandy artifacts (default: `.dandy`)
- `LLM_CONFIGS`: Dictionary of LLM configurations
- `CACHE_MEMORY_LIMIT`: Memory cache item limit
- `CACHE_SQLITE_DATABASE_PATH`: SQLite cache path
- `HTTP_CONNECTION_RETRY_COUNT`: HTTP retry attempts
- `DEBUG`: Enable debug mode

**Environment variable:**
```bash
export DANDY_SETTINGS_MODULE=dandy_settings
```

## File Organization

### Project Structure

```
project/
├── dandy_settings.py          # Configuration (required)
├── dandy/                     # Dandy source (if contributing)
│   ├── bot/
│   ├── llm/
│   ├── intel/
│   └── recorder/
├── tests/                     # Unit tests
│   ├── bot/
│   ├── llm/
│   └── intel/
├── docs/                      # Documentation
└── example_project/           # Example integration
```

### Example Project

See `tests/example_project/` for a complete working example:
- Book generation workflow
- Multiple bots for different tasks
- Complex Intel models
- Workflow orchestration

## Common Pitfalls

### ❌ Avoid These Patterns

1. **Agent module usage** (removed in v2.0.0)
   ```python
   # Don't do this
   class MyAgent(Agent):  #-agent is removed
       processors = (Bot1, Bot2)
   
   # Do this instead
   class MyBot(Bot):
       def __post_init__(self):
           self.bot1 = Bot1()
           self.bot2 = Bot2()
       
       def process(self, input):
           result1 = self.bot1.process(input)
           return self.bot2.process(result1)
   ```

2. **Overriding __getattribute__** in Bot subclasses
   - The Bot class already wraps `process()` with recorder events
   - Custom `__getattribute__` interferes with this

3. **Non-string decoder keys**
   ```python
   # Don't do this
   decoder.prompt_to_values(
       keys_values={1: 'one', 2: 'two'}  # Keys must be strings
   )
   
   # Do this
   decoder.prompt_to_values(
       keys_values={'1': 'one', '2': 'two'}
   )
   ```

4. **Missing super().__post_init__()**
   ```python
   # Don't do this
   class MyBot(Bot):
       def __post_init__(self):
           self.custom_init()  # Missing super call
   
   # Do this
   class MyBot(Bot):
       def __post_init__(self):
           super().__post_init__()  # Always call first
           self.custom_init()
   ```

5. **Direct recorder manipulation**
   ```python
   # Don't do this
   bot._recorder_called = True  # Internal state
   
   # Do this
   bot.process(prompt)  # Recorder events are automatic
   ```

### ✅ Do These Instead

1. **Use Prompt for complex formatting**
   ```python
   prompt = Prompt().heading('Task').list(tasks)
   ```

2. **Leverage mixins**
   ```python
   class MyBot(Bot):
       def process(self):
           self.http.get(url)  # HTTP service
           self.file.read(path)  # File service
   ```

3. **Test with multiple configs**
   ```python
   @run_llm_configs()
   def test_feature(self, llm_config):
       bot = MyBot(llm_config=llm_config)
   ```

4. **Use Intel for structured data**
   ```python
   class ResultIntel(BaseIntel):
       value: int
       confidence: float
   ```

## Documentation Standards

### Docstring Style

Use Sphinx/Google-style docstrings:

```python
class MyBot(Bot):
    """Bot for processing user requests.
    
    Provides custom processing logic with error handling
    and detailed logging capabilities.
    """
    
    def process(self, user_input: Prompt | str) -> BaseIntel:
        """Process a user prompt and return Intel.
        
        Args:
            user_input: The user's input as a Prompt or string.
        
        Returns:
            BaseIntel: The processed result as Intel.
        
        Raises:
            ValueError: If prompt processing fails.
        """
        return self.llm.prompt_to_intel(prompt=user_input)
```

### Type Hinting

Always use type hints:

```python
from typing import Any

def process(
    self,
    user_input: Prompt | str,  # Union types with |
    config: dict[str, Any],    # Generic types
    *args: str,                 # Variadic args
    **kwargs: int,              # Keyword args
) -> BaseIntel | None:         # Return type
    ...
```

## CI/CD & Quality Tools

### Ruff Configuration

The project uses Ruff with these key settings:
- **Target version**: py311
- **Line length**: 88
- **Quote style**: single
- **Select**: ALL rules (with specific exceptions in `ruff.toml`)

### Before Merging

Ensure:
1. ✅ All unit tests pass: `just run-tests`
2. ✅ Documentation builds: `just run-doc-tests`
3. ✅ Code passes Ruff linting: `ruff check .`
4. ✅ Code passes Ruff formatting: `ruff format .`
5. ✅ No spelling errors: `codespell .`
6. ✅ Type hints are complete
7. ✅ Tests cover new functionality
8. ✅ Documentation updated

### Linting Commands

```bash
# Run linter
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .

# Run tests
python -m unittest discover -v ./tests

# Build documentation
mkdocs build --strict
```

## Quick Reference

### Import Paths

```python
from dandy import (
    Bot,
    Prompt,
    BaseIntel,
    BaseListIntel,
    Recorder,
    MemoryCache,
    SqliteCache,
    cache_to_memory,
    cache_to_sqlite,
)

from dandy.core.exceptions import DandyError, DandyCriticalError, DandyRecoverableError
from dandy.intel.intel import BaseIntel
from dandy.llm.prompt.prompt import Prompt
from dandy.recorder.recorder import Recorder
```

### Common Operations

```python
# Create a bot
bot = Bot(llm_config='DEFAULT', llm_temperature=0.7)

# Create a prompt
prompt = Prompt().heading('Title').text('Content')

# Process with Intel
result = bot.process(prompt, intel_class=MyIntel)

# Cache results
@cache_to_memory()
def expensive_operation():
    ...

# Start recording
Recorder.start_recording('session_name')
bot.process(prompt)
Recorder.stop_recording('session_name')
Recorder.to_html_file('session_name')
```

### Template for New Bot

```python
from dandy import Bot, Prompt, BaseIntel
from dandy.core.exceptions import DandyError


class NewBot(Bot):
    """Short description of what this bot does."""
    
    llm_config = 'DEFAULT'
    role = 'Assistant'
    task = 'Provide helpful responses based on user input.'
    
    def __post_init__(self):
        super().__post_init__()
        # Custom initialization here
    
    def process(self, user_input: Prompt | str) -> BaseIntel:
        """Process the user's input and return Intel.
        
        Args:
            user_input: The user's input as a Prompt or string.
        
        Returns:
            BaseIntel: The processed result.
        
        Raises:
            DandyError: If processing fails.
        """
        if not user_input:
            raise DandyError('user_input cannot be empty')
        
        return self.llm.prompt_to_intel(prompt=user_input)
```
