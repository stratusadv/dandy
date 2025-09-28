# Project / Module Structure

Working with intelligence will become an overwhelming task as you now have to keep two or more scopes in your head when developing.
This is the recommended project / module structure for you to follow that helps keep your code organized and easy to understand.

!!! info

    Check out the [Example](https://github.com/stratusadv/dandy/tree/main/example){:target="_blank"} project to view and understand the structure in more detail.

## Basic Structure

Below is a simple example of the recommended structure for a basic project / module.

``` title="Basic Project / Module Structure" 

📁 book/ <-- This would be for each of your modules
 ├── 📄 __init__.py
 ├── 📄 models.py
 ├── 📄 your_code.py
 ├── 📄 ...
 └── 📁 intelligence/ <-- Dandy related code should be in this directory
      ├── 📄 __init__.py
      ├── 📄 agents.py
      ├── 📄 bots.py
      ├── 📄 intel.py
      ├── 📄 decoders.py
      ├── 📄 prompts.py
      └── 📄 ...
📄 __init__.py
📄 dandy_settings.py
📄 main.py
📄 ...

```

## Advanced Structure

Below is a more advanced example with comments of the recommended structure for more complete projects / modules.

``` title="Advanced Project / Module Structure" 

📁 book/ <-- This would be for each of your modules
 ├── 📄 __init__.py
 ├── 📄 models.py
 ├── 📄 tools.py
 ├── 📄 your_code.py
 ├── 📄 ...
 └── 📁 intelligence/ <-- Dandy related code should be in this directory
      ├── 📁 bots/
      │    ├── 📄 __init__.py
      │    ├── 📄 book_start_bot.py <-- This file should contain one bot alone (can include, intels and prompts specific to this bot)
      │    └── 📄 ...
      ├── 📁 chapter/
      │    ├── 📁 bots/
      │    │    ├── 📄 __init__.py
      │    │    ├── 📄 chapter_content_bot.py <-- This file should also contain one bot alone (can include, intels and prompts specific to this bot)
      │    │    ├── 📄 chapter_structure_bot.py
      │    │    ├── 📄 scene_bot.py
      │    │    └── 📄 ...
      │    ├── 📄 __init__.py
      │    ├── 📄 intel.py <-- Intel Classes in all of these files must be postfixed with "Intel" ex: "SelectIntel"
      │    ├── 📄 prompts.py
      │    └── 📄 ...
      ├── 📁 character/
      │    ├── 📁 bots/
      │    │    ├── 📄 __init__.py
      │    │    ├── 📄 character_description_bot.py
      │    │    └── 📄 ...
      │    ├── 📄 __init__.py
      │    ├── 📄 enums.py <-- Add other related code to the intelligence module to improve separation of concerns
      │    ├── 📄 intel.py
      │    ├── 📄 prompts.py
      │    ├── 📄 workflow.py
      │    └── 📄 ...
      ├── 📁 plot/
      │    ├── 📁 bots/
      │    │    ├── 📄 __init__.py
      │    │    ├── 📄 plot_outline_bot.py
      │    │    ├── 📄 plot_point_description_bot.py
      │    │    └── 📄 ...
      │    ├── 📁 decoders/
      │    │    ├── 📄 __init__.py
      │    │    ├── 📄 plot_guide_decoder.py <- If a file gets to busy, modularize anything to make it easier to follow
      │    │    └── 📄 ...
      │    ├── 📄 __init__.py
      │    ├── 📄 intel.py
      │    ├── 📄 prompts.py <-- All of the plot prompts in this file can be used across the project
      │    └── 📄 ...
      ├── 📁 world/
      │    ├── 📄 __init__.py
      │    ├── 📄 agents.py <-- This would be for Agents that thinks of worlds
      │    ├── 📄 bots.py
      │    ├── 📄 decoders.py
      │    ├── 📄 intel.py
      │    └── 📄 ...
      ├── 📄 __init__.py
      ├── 📄 bots.py <-- This file should contain a Bot class that is used to orchestrate a multi step process as it's in the base of the intelligence
      ├── 📄 intel.py
      ├── 📄 prompts.py
      └── 📄 ...
📄 __init__.py
📄 dandy_settings.py <-- Contains Settings, LLM configs for the entire project
📄 main.py <-- Main entry point for the project
📄 ...

```
