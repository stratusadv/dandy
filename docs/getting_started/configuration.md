# Configuration

## Environment Variables

It's highly recommended that you have a `DANDY_SETTINGS_MODULE` in your environment variables pointed towards your dandy settings module.

```bash
export DANDY_SETTINGS_MODULE=dandy_settings
```

If no environment variable is set, it will look for `dandy_settings` module in the current working directory, python path or sys path.

## Creating a Settings File

In the virtual environment you can run the dandy cli with no arguments to create a settings file.

```bash
dandy
```

The default settings file will be created where the environment variable `DANDY_SETTINGS_MODULE` is set to.

If it is not set the default will be `dandy_settings` in the current working directory.

## Default Settings File

```py title="default_settings.py"
--8<-- "dandy/default_settings.py"
```

You can also copy the default settings file from Github at [`https://github.com/stratusadv/dandy/blob/main/dandy/default_settings.py`](https://github.com/stratusadv/dandy/blob/main/dandy/default_settings.py).

## Your Settings File

After configuring your settings, your file should look something like this.

```py title="dandy_settings.py"
--8<-- "dandy_settings.py"
```
