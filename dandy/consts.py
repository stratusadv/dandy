__VERSION__ = '1.3.4'

# Cache

SQLITE_CACHE_TABLE_NAME = 'cache'
SQLITE_CACHE_DB_NAME = 'dandy_cache.db'
CACHE_DEFAULT_NAME: str = 'dandy'
CACHE_KEY_HASH_LAYER_LIMIT = 3 # This should be set to 3 as anything higher will pull in unwanted attributes for caching.

# LLM

ESTIMATED_CHARACTERS_PER_TOKEN = 4

# Recording

RECORDER_OUTPUT_DIRECTORY = '.dandy_recorder_output'
RECORDING_DEFAULT_NAME = 'default'
RECORDING_POSTFIX_NAME = '_recording_output'

# Settings

DEFAULT_SETTINGS_MODULE = 'dandy_settings'
DEFAULT_SETTINGS_FILE_NAME = f'{DEFAULT_SETTINGS_MODULE}.py'

# Toolbox

TOOLBOX_OUTPUT_DIRECTORY = '.dandy_toolbox_output'
TOOLBOX_DEFAULT_ENV_FILE_NAMES = [
    'dandy.env',
    'development.env',
    'dev.env',
    '.env',
]

