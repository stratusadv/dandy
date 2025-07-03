# Project / Module Structure

Working with intelligence will become an over whelming task as you now have to keep two or more scopes in mind when developing.
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
      ├── 📄 bot.py
      ├── 📄 intel.py
      ├── 📄 prompts.py
      ├── 📄 workflow.py 
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
 ├── 📄 your_code.py
 ├── 📄 ...
 └── 📁 intelligence/ <-- Dandy related code should be in this directory
      ├── 📁 bots/
      │    ├── 📄 __init__.py
      │    ├── 📄 book_start_llm_bot.py <-- Should contain one bot alone (can include, intels and prompts specific to this bot)
      │    └── 📄 ...
      ├── 📁 chapter/
      │    ├── 📁 bots/
      │    │    ├── 📄 __init__.py
      │    │    ├── 📄 chapter_content_llm_bot.py <-- Should contain one bot alone (can include, intels and prompts specific to this bot)
      │    │    ├── 📄 chapter_structure_llm_bot.py
      │    │    ├── 📄 scene_llm_bot.py
      │    │    └── 📄 ...
      │    ├── 📄 __init__.py
      │    ├── 📄 intel.py <-- Intel Classes in all of these files must be postfixed with "Intel" ex: "SelectIntel"
      │    ├── 📄 prompts.py
      │    ├── 📄 workflow.py
      │    └── 📄 ...
      ├── 📁 character/
      │    ├── 📁 bots/
      │    │    ├── 📄 __init__.py
      │    │    ├── 📄 character_description_llm_bot.py
      │    │    └── 📄 ...
      │    ├── 📄 __init__.py
      │    ├── 📄 enums.py <-- Containing all code related to the intelligence work improves separation of concerns
      │    ├── 📄 intel.py
      │    ├── 📄 prompts.py
      │    ├── 📄 workflow.py
      │    └── 📄 ...
      ├── 📁 plot/
      │    ├── 📁 bots/
      │    │    ├── 📄 __init__.py
      │    │    ├── 📄 plot_outline_llm_bot.py
      │    │    ├── 📄 plot_point_description_llm_bot.py
      │    │    └── 📄 ...
      │    ├── 📄 __init__.py
      │    ├── 📄 intel.py
      │    ├── 📄 prompts.py <-- All of the plot prompts in this file can be used across the project
      │    ├── 📄 workflow.py
      │    └── 📄 ...
      ├── 📁 world/
      │    ├── 📄 __init__.py
      │    ├── 📄 bot.py
      │    ├── 📄 intel.py
      │    └── 📄 ...
      ├── 📄 __init__.py
      ├── 📄 intel.py
      ├── 📄 prompts.py
      ├── 📄 workflow.py <-- Should contain a Workflow class that is used to orchestrate a multi step process
      └── 📄 ...
📄 __init__.py
📄 dandy_settings.py <-- Contains Settings, LLM configs for the entire project
📄 main.py <-- Main entry point for the project
📄 ...

```
