import os
from pathlib import Path


def load_environment_variables():
    env_file = f"{Path(__file__).parent.resolve()}/development.env"
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                key, value = line.strip().split("=", 1)
                os.environ[key] = value


def set_python_path():
    pass

def unset_python_path():
    pass