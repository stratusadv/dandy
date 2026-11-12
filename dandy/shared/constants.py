__VERSION__ = '3.0.0a4'

# Cache

SQLITE_CACHE_TABLE_NAME = 'cache'
SQLITE_CACHE_DB_NAME = 'cache.db'
CACHE_DEFAULT_NAME: str = 'dandy'
CACHE_KEY_HASH_LAYER_LIMIT = (
    3  # This should be set to 3 as anything higher will pull in unwanted attributes for caching.
)

# Recording

RECORDING_OUTPUT_DIRECTORY = 'recordings'
RECORDING_DEFAULT_NAME = 'default'
RECORDING_POSTFIX_NAME = '_recording'

# Settings

DEFAULT_SETTINGS_MODULE = 'dandy_settings'

DANDY_JSON_FILE_NAME = 'dandy.json'
DANDY_HOME_CONFIG_DIRECTORY_NAME = 'dandy'
DANDY_LOCAL_DIRECTORY_NAME = f'.{DANDY_HOME_CONFIG_DIRECTORY_NAME}'

# CLI

CLI_WORKING_DIRECTORY = 'cli'

# Agent

AGENT_WORKING_DIRECTORY = 'agent'
SESSIONS_DIRECTORY_NAME = 'sessions'
AGENTS_MD_FILE_NAME = 'AGENTS.md'
