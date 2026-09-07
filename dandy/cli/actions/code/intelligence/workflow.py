from dandy.cli.actions.code.intelligence.bots.coding_bot import CodingBot
from dandy.cli.tui.tui import tui
from dandy.recorder.decorators import recorder_to_html_file


@recorder_to_html_file('code_project_workflow')
def code_project_workflow(user_input: str) -> str:
    start_time = tui.printer.start_task('Implementing', 'your coding request')

    coding_intel = CodingBot().process(user_input)

    tui.printer.end_task(start_time)

    return coding_intel.text
