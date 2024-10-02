from dandy.debug.debug import DebugRecorder
from example.pirate.intelligence.workflow.pirate_story_workflow import PirateStoryWorkflow


if __name__ == '__main__':
    DebugRecorder.start_recording()

    try:
        print(PirateStoryWorkflow.process('N/A'))

    except:
        import traceback
        traceback.print_exc()

    finally:
        DebugRecorder.stop_recording()

        DebugRecorder.to_html_file()