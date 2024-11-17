from importlib.machinery import SourceFileLoader
from pathlib import Path


CURRENT_PATH = Path.cwd()
DANDY_SETTINGS_PATH = CURRENT_PATH / 'dandy_settings.py'

if not Path(DANDY_SETTINGS_PATH).is_file():
    print('You need to create a "dandy_settings.py" file in the current directory.')

_settings = SourceFileLoader('dandy_settings', str(DANDY_SETTINGS_PATH)).load_module()

if _settings.DEFAULT_LLM_CONFIG is None:
    print('You need a DEFAULT_LLM_CONFIG in your "dandy_settings.py".')

DEFAULT_LLM_CONFIG = _settings.DEFAULT_LLM_CONFIG