import os

CLI_OUTPUT_DIRECTORY = '.dandy_cli_output'

CLI_DEFAULT_ENV_FILE_NAMES = [
    'dandy.env',
    'development.env',
]

DEBUG_OUTPUT_DIRECTORY = '.dandy_debug_output'

ESTIMATED_CHARACTERS_PER_TOKEN = 4

DANDY_SETTINGS_MODULE = 'dandy_settings' if os.getenv('DANDY_SETTINGS_MODULE', None) is None else os.getenv('DANDY_SETTINGS_MODULE')
