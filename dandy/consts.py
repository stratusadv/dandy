__VERSION__ = '1.0.0a1'

# Cache

SQLITE_CACHE_TABLE_NAME = 'cache'
SQLITE_CACHE_DB_NAME = 'dandy_cache.db'
DEFAULT_CACHE_NAME: str = 'dandy'
HASH_KEY_LAYER_LIMIT = 2 # This should be set to 2 as right now the services have no instances on the first instance.

# CLI

CLI_OUTPUT_DIRECTORY = '.dandy_cli_output'
CLI_DEFAULT_ENV_FILE_NAMES = [
    'dandy.env',
    'development.env',
    'dev.env',
    '.env',
]

# Debug

RECORDER_OUTPUT_DIRECTORY = '.dandy_recorder_output'
RECORDING_DEFAULT_NAME = 'default'
RECORDING_POSTFIX_NAME = '_recording_output'

# LLM

ESTIMATED_CHARACTERS_PER_TOKEN = 4

# Settings

DEFAULT_SETTINGS_MODULE = 'dandy_settings'
DEFAULT_SETTINGS_FILE_NAME = f'{DEFAULT_SETTINGS_MODULE}.py'

