import contextlib
import io
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from blessed import Terminal

from dandy.application.agent.session import session
from dandy.interfaces.cli.tui.markdown import MarkdownRenderer
from dandy.interfaces.cli.tui.printer import Printer


class TestMarkdownRenderer(TestCase):
    def setUp(self) -> None:
        self.renderer = MarkdownRenderer(Terminal(), width=40)

    def test_render_empty_markdown_returns_empty_string(self) -> None:
        self.assertEqual(self.renderer.render(''), '')

    def test_render_plain_paragraph_wraps_to_terminal_width(self) -> None:
        rendered = self.renderer.render('word ' * 30)

        self.assertGreater(len(rendered.splitlines()), 1)
        self.assertIn('word', rendered)

    def test_render_heading_adds_divider_under_h1_and_h2(self) -> None:
        rendered = self.renderer.render('# Title\n\n## Subtitle')

        self.assertIn('Title', rendered)
        self.assertIn('Subtitle', rendered)
        self.assertIn('─' * 40, rendered)

    def test_render_inline_styles_remove_markdown_markers(self) -> None:
        rendered = self.renderer.render('**bold** *italic* `code`')

        self.assertIn('bold', rendered)
        self.assertIn('italic', rendered)
        self.assertIn('code', rendered)
        self.assertNotIn('**', rendered)
        self.assertNotIn('`', rendered)

    def test_render_link_shows_label_and_url(self) -> None:
        rendered = self.renderer.render('[docs](https://dandy.dev)')

        self.assertIn('docs', rendered)
        self.assertIn('https://dandy.dev', rendered)

    def test_render_unordered_list_uses_bullets(self) -> None:
        rendered = self.renderer.render('- one\n- two')

        self.assertIn('• one', rendered)
        self.assertIn('• two', rendered)

    def test_render_ordered_list_keeps_numbering(self) -> None:
        rendered = self.renderer.render('1. first\n2. second')

        self.assertIn('1. first', rendered)
        self.assertIn('2. second', rendered)

    def test_render_nested_list_indents_sub_items(self) -> None:
        rendered = self.renderer.render('- top\n  - nested')

        self.assertIn('• top', rendered)
        self.assertIn('  • nested', rendered)

    def test_render_code_fence_preserves_lines(self) -> None:
        source = '```python\ndef f():\n    return 1\n```'
        rendered = self.renderer.render(source)

        self.assertIn('python', rendered)
        self.assertIn('def f():', rendered)
        self.assertIn('return 1', rendered)

    def test_render_blockquote_prefixes_a_bar(self) -> None:
        rendered = self.renderer.render('> wise words')

        self.assertIn('│', rendered)
        self.assertIn('wise words', rendered)

    def test_render_horizontal_rule_prints_a_divider(self) -> None:
        rendered = self.renderer.render('---')

        self.assertIn('─' * 10, rendered)

    def test_render_strips_html_tags(self) -> None:
        rendered = self.renderer.render('<b>hello</b> there')

        self.assertIn('hello', rendered)
        self.assertNotIn('<b>', rendered)

    def test_render_table_builds_a_box(self) -> None:
        source = '| Name | Qty |\n| --- | ---: |\n| Nail | 12 |'
        rendered = self.renderer.render(source)

        self.assertIn('Name', rendered)
        self.assertIn('Qty', rendered)
        self.assertIn('Nail', rendered)
        self.assertIn('┌', rendered)
        self.assertIn('└', rendered)

    def test_render_table_right_aligns_numeric_columns(self) -> None:
        source = '| Item | Qty |\n| --- | ---: |\n| Nail | 12 |\n| Bolt | 100 |'
        rendered = self.renderer.render(source)
        lines = rendered.splitlines()

        self.assertIn(' 12 │', lines[3])
        self.assertIn('100 │', lines[4])

    def test_render_table_border_matches_row_widths(self) -> None:
        source = '| agent | pass | mean wall |\n| --- | --- | --- |\n| dandy | 2/3 | 349s |'
        rendered = self.renderer.render(source)
        lines = rendered.splitlines()

        self.assertEqual(len(lines), 5)
        self.assertEqual(len({self.renderer.term.length(line) for line in lines}), 1)

    def test_render_mixed_document_keeps_block_order(self) -> None:
        source = '# Build\n\nRun the steps:\n\n- make\n- test\n\n```sh\necho ok\n```\n\nDone.'
        rendered = self.renderer.render(source)

        self.assertLess(rendered.index('Build'), rendered.index('make'))
        self.assertLess(rendered.index('make'), rendered.index('echo ok'))
        self.assertLess(rendered.index('echo ok'), rendered.index('Done.'))


class TestMarkdownFileLinks(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.project_base_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.project_base_path
        self.renderer = MarkdownRenderer(Terminal(force_styling='default'), width=40)

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()

    def _expected_link(self, relative_path: str) -> str:
        expected_uri = (self.project_base_path / relative_path).as_uri()
        return f'\x1b]8;;{expected_uri}\x1b\\{relative_path}\x1b]8;;\x1b\\'

    def test_paragraph_path_is_linked(self) -> None:
        rendered = self.renderer.render('I edited src/foo.py today.')

        self.assertIn(self._expected_link('src/foo.py'), rendered)

    def test_inline_code_span_path_is_linked(self) -> None:
        rendered = self.renderer.render('I edited `src/foo.py` today.')

        self.assertIn(self._expected_link('src/foo.py'), rendered)

    def test_bold_span_path_is_linked(self) -> None:
        rendered = self.renderer.render('**src/foo.py** was touched.')

        self.assertIn(self._expected_link('src/foo.py'), rendered)

    def test_list_item_path_is_linked(self) -> None:
        rendered = self.renderer.render('- touched src/foo.py')

        self.assertIn(self._expected_link('src/foo.py'), rendered)

    def test_table_cell_path_is_linked(self) -> None:
        rendered = self.renderer.render('| file |\n| --- |\n| src/foo.py |')

        self.assertIn(self._expected_link('src/foo.py'), rendered)

    def test_heading_path_is_linked(self) -> None:
        rendered = self.renderer.render('## Changes to src/foo.py')

        self.assertIn(self._expected_link('src/foo.py'), rendered)

    def test_url_is_not_linked(self) -> None:
        rendered = self.renderer.render('See https://example.com/docs for details.')

        self.assertNotIn('\x1b]8;;', rendered)
        self.assertIn('https://example.com/docs', rendered)

    def test_fenced_code_block_is_not_linked(self) -> None:
        rendered = self.renderer.render('```\nfrom src.stockroom.ops import run\n```')

        self.assertNotIn('\x1b]8;;', rendered)
        self.assertIn('src.stockroom.ops', rendered)

    def test_wrapped_paragraph_keeps_links_intact(self) -> None:
        long_paragraph = ' '.join(f'src/file{i}.py' for i in range(10)) + ' and more words here'

        rendered = self.renderer.render(long_paragraph)
        lines = rendered.splitlines()

        self.assertGreater(len(lines), 1)

        for line in lines:
            self.assertEqual(line.count('\x1b]8;;file'), line.count('\x1b]8;;\x1b\\'))

        for index in range(10):
            self.assertIn(f'src/file{index}.py', '\n'.join(lines))


class TestPrinterMarkdownOutput(TestCase):
    def test_output_prints_rendered_markdown(self) -> None:
        printer = Printer(Terminal())

        with contextlib.redirect_stdout(io.StringIO()) as buffer:
            printer.output('# Title\n\nPlain text.')

        captured = buffer.getvalue()

        self.assertIn('Title', captured)
        self.assertNotIn('# ', captured)
