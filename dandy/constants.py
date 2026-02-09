__VERSION__ = '2.0.0'

# Cache

SQLITE_CACHE_TABLE_NAME = 'cache'
SQLITE_CACHE_DB_NAME = 'dandy_cache.db'
CACHE_DEFAULT_NAME: str = 'dandy'
CACHE_KEY_HASH_LAYER_LIMIT = 3 # This should be set to 3 as anything higher will pull in unwanted attributes for caching.

# LLM

ESTIMATED_CHARACTERS_PER_TOKEN = 3.2 # This is set to be more conservative to account for logic containing a lot of symbols.

# Recording

RECORDING_OUTPUT_DIRECTORY = 'recordings'
RECORDING_DEFAULT_NAME = 'default'
RECORDING_POSTFIX_NAME = '_recording'

# Settings

DEFAULT_SETTINGS_MODULE = 'dandy_settings'
DEFAULT_SETTINGS_FILE_NAME = f'{DEFAULT_SETTINGS_MODULE}.py'

# CLI

CLI_WORKING_DIRECTORY = 'cli'
CLI_DEFAULT_ENV_FILE_NAMES = [
    'dandy.env',
    'development.env',
    'dev.env',
    '.env',
]

