from unittest import TestCase

from dandy.interfaces.cli.tui.text import wrap_text_with_indentation


class TestWrapTextWithIndentation(TestCase):
    def test_short_text_is_unchanged(self) -> None:
        self.assertEqual(wrap_text_with_indentation('hello world', width=70), 'hello world')

    def test_long_line_wraps_at_width(self) -> None:
        text = ' '.join(f'word{index}' for index in range(10))

        wrapped = wrap_text_with_indentation(text, width=20)

        self.assertNotEqual(wrapped, text)
        for line in wrapped.split('\n'):
            self.assertLessEqual(len(line), 20)

    def test_indentation_is_preserved_on_wrapped_lines(self) -> None:
        wrapped = wrap_text_with_indentation('    first second third fourth', width=16)

        self.assertEqual(wrapped, '    first second\n    third fourth')

    def test_blank_lines_between_paragraphs_are_kept(self) -> None:
        self.assertEqual(
            wrap_text_with_indentation('one two\n\nthree four', width=70),
            'one two\n\nthree four',
        )

    def test_blank_line_inside_a_paragraph_is_kept(self) -> None:
        self.assertEqual(
            wrap_text_with_indentation('one two\n\n\nthree four', width=70),
            'one two\n\n\nthree four',
        )

    def test_long_words_are_not_broken(self) -> None:
        long_word = 'x' * 40

        wrapped = wrap_text_with_indentation(long_word, width=10)

        self.assertEqual(wrapped, long_word)
