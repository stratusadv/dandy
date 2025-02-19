# Project Structure

Working with intelligence will become an over whelming task as you now have to keep two or more scopes in mind when developing.
This is the recommended project structure for you to follow that helps keep your code organized and easy to understand.

## Recommended Structure

```
cookie_recipe/ <-- This would be for each of your modules
    __init__.py
    your_code.py
    ...
    ...
    intelligence/ <-- Dandy related code should be in this directory
        __init__.py
        bots/
            __init__.py
            cookie_recipe_llm_bot.py <-- Should contain one bot alone (can include, intels and prompts specific to this bot)
            cookie_recipe_safety_llm_bot.py
            cookie_recipe_review_llm_bot.py
            ...
            ...
        intel/
            __init__.py
            cookie_recipe_intel.py <-- Intel Classes in all of these files must be postfixed with "Intel" ex: "SelectIntel"
            cookie_recipe_story_intel.py
            cookie_recipe_marketing_intel.py
            ...
            ...
        prompts/
            __init__.py
            cookie_recipe_prompts.py <-- All of these files would contain prompts that would be shared across the project
            cookie_recipe_email_prompts.py
            cookie_recipe_instructions_prompts.py
            ...
            ...     
        workflows/
            __init__.py
            cookie_recipe_generation_workflow.py <-- In most cases this workflow would be used to interact with the user
            ...
            ...

dandy_settings.py <-- Contains Settings, LLM configs for the entire project
```
