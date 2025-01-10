from pathlib import Path

from dandy.debug.debug import DebugRecorder
from example.pirate.intelligence.workflow.pirate_story_workflow import PirateStoryWorkflow, PirateStoryWithFuturesWorkflow


if __name__ == '__main__':
    DebugRecorder.start_recording('pirate_story_example')

    try:
        print(PirateStoryWorkflow.process('N/A'))
        # print(PirateStoryWithFuturesWorkflow.process('N/A'))

    except:
        import traceback
        traceback.print_exc()

    finally:
        DebugRecorder.stop_all_recording()

        DebugRecorder.to_html_file(
            debugger_name='pirate_story_example',
        )