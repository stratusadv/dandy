<div align="center">
    <a href="https://dandysoftware.com">
        <img alt="Dandy Logo" src="https://dandysoftware.com/static/img/dandy_icon_128.png"/>
    </a>
</div>

# Dandy

![Build](https://img.shields.io/github/actions/workflow/status/stratusadv/dandy/run_tests.yml)
![Python Versions](https://img.shields.io/pypi/pyversions/dandy)
![PyPI Version](https://img.shields.io/pypi/v/dandy)
![Downloads](https://img.shields.io/pypi/dm/dandy)

A powerful open-source Python framework that simplifies the development of artificial intelligence software.

### Get Started

Start by installing with `pip install dandy` and then checking out our [quick start guide](https://dandysoftware.com/getting_started/quick_start/) for more steps.

### Documentation

Check out the [Dandy Website](https://dandysoftware.com) for documentation including tutorials and more.

### Command Line

The `dandy` command runs the coding assistant against the current project. Run it from your project root (where `dandy_settings.py` lives). If no `dandy_settings.py` exists, dandy will instead load settings from a `dandy.json` file found in `.dandy/dandy.json` in the current directory, or `~/.config/dandy/dandy.json` as a last resort before creating a settings file for you.

```bash
dandy                          # start an interactive agentic loop
dandy "fix the failing tests"  # run one request, then exit
dandy -h                       # show usage
```

Inside the interactive session every message goes to the coding agent. `/clear` resets the conversation, and pressing `escape` twice (or `/quit`) exits the loop. Use the one-shot form when you only want a single answer without entering the REPL.

The CLI's model is set with `CLI_CONFIG` in `dandy_settings.py`, e.g. `CLI_CONFIG = {'CODING': 'DEFAULT'}` points the coding agent at the `DEFAULT` entry in `LLM_CONFIGS`.

The same settings can be expressed as JSON when you don't want a Python module. Keys are case-insensitive at the top level (`llm_configs` === `LLM_CONFIGS`), so a minimal `.dandy/dandy.json` looks like:

```json
{
  "llm_configs": {
    "default": {
      "host": "api.example.com",
      "api_key": "your-key",
      "model": "your-model"
    }
  },
  "cli_config": {"coding": "default"}
}
```

