__VERSION__ = '0.12.0'

# Cache

SQLITE_CACHE_TABLE_NAME = 'cache'
DEFAULT_CACHE_NAME: str = 'dandy'

# CLI

CLI_OUTPUT_DIRECTORY = '.dandy_cli_output'
CLI_DEFAULT_ENV_FILE_NAMES = [
    'dandy.env',
    'development.env',
    'dev.env',
    '.env',
]

# Debug

DEBUG_OUTPUT_DIRECTORY = '.dandy_debug_output'

# LLM

ESTIMATED_CHARACTERS_PER_TOKEN = 4

# Settings

DEFAULT_SETTINGS_MODULE = 'dandy_settings'
DEFAULT_SETTINGS_FILE_NAME = f'{DEFAULT_SETTINGS_MODULE}.py'

