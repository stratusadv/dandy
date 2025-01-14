from dandy.debug.debug import DebugRecorder
from dandy.llm import Prompt

from example.cookie.intelligence.bots.cookie_recipe_llm_bot import CookieRecipeLlmBot



if __name__ == '__main__':
    DebugRecorder.start_recording('cookie_example')

    try:
        cookie_recipe_intel = CookieRecipeLlmBot.process(
            prompt=Prompt().text('I love broccoli and oatmeal!'),
        )

        print(cookie_recipe_intel.model_dump_json(indent=4))
    except:
        import traceback
        traceback.print_exc()

    finally:
        DebugRecorder.stop_all_recording()

        DebugRecorder.to_html_file(
            debugger_name='cookie_example',
        )
