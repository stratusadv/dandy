import threading
from time import sleep
from typing import Callable
from unittest import TestCase, mock

from blessed import Terminal

from dandy.cli.tui.printer import Printer, _TaskProgress


class TestPrinterStepTimings(TestCase):
    def setUp(self) -> None:
        self.printer = Printer(Terminal())

        self.stdout_patch = mock.patch('sys.stdout.write')
        self.mock_write = self.stdout_patch.start()
        self.addCleanup(self.stdout_patch.stop)

        self.print_patch = mock.patch('builtins.print')
        self.mock_print = self.print_patch.start()
        self.addCleanup(self.print_patch.stop)

    def test_completed_frame_shows_duration_in_green(self) -> None:
        progress = _TaskProgress(Terminal(), step_indent=2)
        frame = progress.completed_frame('Thinking', 2.3)

        self.assertIn('Thinking took 2.3s', frame)
        self.assertIn(progress.term.green, frame)

    def test_run_timed_task_reports_each_step_timing(self) -> None:
        release = threading.Event()

        def work(update: Callable[[str], None]) -> object:
            update('Thinking')
            sleep(0.25)
            update('Running get_weather')
            release.wait()
            return {'text': 'done'}

        threading.Timer(0.6, release.set).start()

        result = self.printer.run_timed_task(action_name='Coding', task='fix bug', work=work)

        self.assertEqual(result, {'text': 'done'})

        printed_lines = [str(call.args[0]) for call in self.mock_print.call_args_list if call.args]
        completion_lines = [line for line in printed_lines if ' took ' in line]

        self.assertGreaterEqual(len(completion_lines), 2)
        self.assertTrue(any('Thinking took ' in line for line in completion_lines))
        self.assertTrue(any('Running get_weather took ' in line for line in completion_lines))
