from __future__ import annotations

import re
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from blessed import Terminal


def _looks_numeric(text: str) -> bool:
    return re.match(r'^\s*[-+]?\d[\d,.]*\s*$', text) is not None


class MarkdownRenderer:
    """Render common markdown constructs into terminal-styled text.

    A tiny, dependency-free renderer for the CLI's final-answer output. It
    styles headings, inline emphasis, fenced code blocks, lists, blockquotes,
    horizontal rules, and pipe tables on top of the ``blessed`` Terminal the
    CLI already uses, so no extra library is required.
    """

    _FENCE_PATTERN = re.compile(r'^(?P<fence>`{3,}|~{3,})\s*(?P<lang>\w*)\s*$')
    _HEADING_PATTERN = re.compile(r'^(?P<hashes>#{1,6})\s+(?P<text>.*)$')
    _HR_PATTERN = re.compile(r'^\s*(?P<marker>[-*_])\s*(?:(?P=marker)\s*){2,}$')
    _LIST_ITEM_PATTERN = re.compile(r'^\s*(?P<marker>[-*+]|\d+\.)\s+(?P<text>.*)$')
    _TABLE_DELIMITER_PATTERN = re.compile(r'^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)*\|?\s*$')
    _INLINE_ESCAPE_PATTERN = re.compile(r'\\([\\`*_{}\[\]()#+\-.!>|])')
    _INLINE_PATTERN = re.compile(
        r'(?P<code>`[^`\n]+`)'
        r'|(?P<bold>\*\*(?:(?!\*\*).)+\*\*)'
        r'|(?P<strike>~~(?:(?!~~).)+~~)'
        r'|(?P<image>!\[[^\]\n]*\]\([^)\n]+\))'
        r'|(?P<link>\[[^\]\n]+\]\([^)\n]+\))'
        r'|(?P<italic>(?<!\w)[*_](?![*_\s])(?:(?![*_]).)+[*_])(?!\w)'
        r'|(?P<html></?[a-zA-Z][^>]*>)'
    )
    _HTML_TAGS: dict[str, str] = {
        '<br>': ' ',
        '<br/>': ' ',
        '<br />': ' ',
        '<p>': '',
        '</p>': '\n\n',
        '<hr>': '',
    }

    def __init__(self, term: Terminal, width: int | None = None) -> None:
        self.term = term
        self.width = width if width is not None else term.width

    def render(self, markdown: str) -> str:
        if not markdown:
            return ''

        rendered = self._render_blocks(markdown.split('\n'))
        return '\n\n'.join(part for part in rendered if part)

    def _render_blocks(self, lines: list[str]) -> list[str]:
        rendered: list[str] = []
        index = 0

        while index < len(lines):
            stripped = lines[index].strip()

            if not stripped:
                index += 1
                continue

            block = self._block_from_lines(lines, index)

            if block is not None:
                kind, data, index = block
                rendered.append(self._render_block(kind, data))
                continue

            paragraph_lines: list[str] = []

            while index < len(lines) and lines[index].strip():
                paragraph_lines.append(lines[index].strip())
                index += 1

            rendered.append(self._render_paragraph(' '.join(paragraph_lines)))

        return rendered

    def _block_from_lines(self, lines: list[str], index: int) -> tuple[str, object, int] | None:
        parsers = (
            ('code', self._parse_code_block),
            ('heading', self._parse_heading),
            ('hr', self._parse_horizontal_rule),
            ('quote', self._parse_blockquote),
            ('list', self._parse_list),
            ('table', self._parse_table),
        )

        for kind, parser in parsers:
            parsed = parser(lines, index)

            if parsed is not None:
                data, next_index = parsed
                return (kind, data, next_index)

        return None

    def _parse_code_block(
        self, lines: list[str], index: int
    ) -> tuple[tuple[str, list[str]], int] | None:
        match = self._FENCE_PATTERN.match(lines[index].strip())

        if match is None:
            return None

        fence = match.group('fence')
        language = match.group('lang')
        code_lines: list[str] = []
        cursor = index + 1

        while cursor < len(lines) and not lines[cursor].strip().startswith(fence[0] * 3):
            code_lines.append(lines[cursor])
            cursor += 1

        return (language, code_lines), cursor + 1

    def _parse_heading(self, lines: list[str], index: int) -> tuple[tuple[int, str], int] | None:
        match = self._HEADING_PATTERN.match(lines[index].strip())

        if match is None:
            return None

        level = len(match.group('hashes'))
        return (level, match.group('text').strip()), index + 1

    def _parse_horizontal_rule(self, lines: list[str], index: int) -> tuple[None, int] | None:
        if self._HR_PATTERN.match(lines[index].strip()) is None:
            return None

        return None, index + 1

    def _parse_blockquote(self, lines: list[str], index: int) -> tuple[list[str], int] | None:
        if not lines[index].strip().startswith('>'):
            return None

        quote_lines: list[str] = []

        while index < len(lines) and lines[index].strip().startswith('>'):
            quote_lines.append(lines[index].lstrip()[1:].strip())
            index += 1

        return quote_lines, index

    def _parse_list(
        self, lines: list[str], index: int
    ) -> tuple[list[tuple[int, str, str]], int] | None:
        if self._LIST_ITEM_PATTERN.match(lines[index]) is None:
            return None

        items: list[tuple[int, str, str]] = []

        while index < len(lines):
            item_match = self._LIST_ITEM_PATTERN.match(lines[index])

            if item_match is None:
                break

            indent = len(lines[index]) - len(lines[index].lstrip())
            marker = item_match.group('marker')
            items.append((indent, marker, item_match.group('text').strip()))
            index += 1

        return items, index

    def _parse_table(
        self, lines: list[str], index: int
    ) -> tuple[tuple[list[str], list[list[str]]], int] | None:
        if not self._table_start(lines, index):
            return None

        header_cells = self._split_table_row(lines[index].strip())
        cursor = index + 2
        body_rows: list[list[str]] = []

        while cursor < len(lines) and lines[cursor].strip() and '|' in lines[cursor]:
            body_rows.append(self._split_table_row(lines[cursor]))
            cursor += 1

        return (header_cells, body_rows), cursor

    def _render_block(self, kind: str, data: object) -> str:
        if kind == 'code':
            language, code_lines = cast('tuple[str, list[str]]', data)
            rendered = self._render_code_block(language, code_lines)
        elif kind == 'heading':
            level, text = cast('tuple[int, str]', data)
            rendered = self._render_heading(level, text)
        elif kind == 'hr':
            rendered = self._render_horizontal_rule()
        elif kind == 'quote':
            rendered = self._render_blockquote(cast('list[str]', data))
        elif kind == 'list':
            rendered = self._render_list(cast('list[tuple[int, str, str]]', data))
        elif kind == 'table':
            header_cells, body_rows = cast('tuple[list[str], list[list[str]]]', data)
            rendered = self._render_table(header_cells, body_rows)
        else:
            rendered = ''

        return rendered

    def _table_start(self, lines: list[str], index: int) -> bool:
        if index + 1 >= len(lines):
            return False

        header = lines[index].strip()
        delimiter = lines[index + 1].strip()

        return (
            '|' in header
            and '|' in delimiter
            and self._TABLE_DELIMITER_PATTERN.match(delimiter) is not None
        )

    @staticmethod
    def _split_table_row(row: str) -> list[str]:
        stripped = row.strip().removeprefix('|').removesuffix('|')
        return [cell.strip() for cell in stripped.split('|')]

    def _render_code_block(self, language: str, code_lines: list[str]) -> str:
        term = self.term
        top = f'{term.bold_blue("┌─")} {term.cyan(language)}' if language else term.bold_blue('┌─')
        rendered = [top]
        bar = term.grey('│ ')

        rendered.extend(
            f'{bar}{term.yellow(code_line)}' if code_line else bar for code_line in code_lines
        )
        rendered.append(term.grey('└─'))

        return '\n'.join(rendered)

    def _render_heading(self, level: int, text: str) -> str:
        term = self.term
        styled = self._apply_inline(text)

        if level == 1:
            return f'{term.bold_cyan(styled)}\n{term.cyan("─" * self.width)}'

        if level == 2:
            return f'{term.bold_blue(styled)}\n{term.blue("─" * self.width)}'

        if level == 3:
            return term.bold_purple(styled)

        return term.bold(styled)

    def _render_horizontal_rule(self) -> str:
        return self.term.bold_grey('─' * self.width)

    def _render_blockquote(self, quote_lines: list[str]) -> str:
        styled = self._apply_inline(' '.join(quote_lines))
        wrapped = self.term.wrap(styled, width=self.width - 2)

        if not wrapped:
            return ''

        bar = self.term.cyan('│ ')
        return '\n'.join(f'{bar}{line}' for line in wrapped)

    def _render_paragraph(self, text: str) -> str:
        styled = self._apply_inline(text)
        return '\n'.join(self.term.wrap(styled, width=self.width))

    def _render_list(self, items: list[tuple[int, str, str]]) -> str:
        rendered: list[str] = []

        for indent, marker, text in items:
            ordered = marker.endswith('.')
            bullet = marker if ordered else self._bullet_for(marker)
            bullet_styled = self.term.cyan(f'{bullet} ')
            indent_width = min(indent, self.width // 2)
            prefix = ' ' * indent_width
            styled = self._apply_inline(text)
            available = max(1, self.width - indent_width - self.term.length(bullet_styled) - 1)
            wrapped = self.term.wrap(styled, width=available)

            if not wrapped:
                wrapped = ['']

            rendered.append(f'{prefix}{bullet_styled}{wrapped[0]}')
            continuation = ' ' * (indent_width + self.term.length(bullet_styled))
            rendered.extend(f'{continuation}{line}' for line in wrapped[1:])

        return '\n'.join(rendered)

    def _render_table(self, header_cells: list[str], body_rows: list[list[str]]) -> str:
        all_rows = [header_cells, *body_rows]
        column_count = max((len(row) for row in all_rows), default=1)
        padded_rows = [row + [''] * (column_count - len(row)) for row in all_rows]
        styled_rows = [[self._apply_inline(cell) for cell in row] for row in padded_rows]
        content_width = max(10, (self.width - column_count * 3 - 1) // column_count)
        column_widths = [
            min(max(self.term.length(row[column]) for row in styled_rows), content_width)
            for column in range(column_count)
        ]
        wrapped_rows = [
            [self.term.wrap(cell, width=column_widths[column]) for column, cell in enumerate(row)]
            for row in styled_rows
        ]
        numeric_rows = [[_looks_numeric(cell) for cell in row] for row in padded_rows]

        rendered = [self._table_separator('┌', '┬', '┐', column_widths)]
        rendered.extend(
            self._table_row_lines(wrapped_rows[0], column_widths, numeric_rows[0], header=True)
        )
        rendered.append(self._table_separator('├', '┼', '┤', column_widths))

        for row_number in range(1, len(wrapped_rows)):
            rendered.extend(
                self._table_row_lines(
                    wrapped_rows[row_number], column_widths, numeric_rows[row_number], header=False
                )
            )

        rendered.append(self._table_separator('└', '┴', '┘', column_widths))

        return '\n'.join(rendered)

    def _table_separator(self, left: str, middle: str, right: str, column_widths: list[int]) -> str:
        border = self.term.grey
        pieces = [border(left)]

        for column in range(len(column_widths)):
            pieces.append(border('─' * column_widths[column]))

            if column < len(column_widths) - 1:
                pieces.append(border(middle))

        pieces.append(border(right))
        return ''.join(pieces)

    def _table_row_lines(
        self,
        wrapped_cells: list[list[str]],
        column_widths: list[int],
        numeric: list[bool],
        header: bool,
    ) -> list[str]:
        term = self.term
        line_count = max((len(cell_lines) for cell_lines in wrapped_cells), default=1)
        rendered: list[str] = []

        for line_index in range(line_count):
            cell_texts: list[str] = []

            for column, cell_lines in enumerate(wrapped_cells):
                cell_text = cell_lines[line_index] if line_index < len(cell_lines) else ''
                visible = term.length(cell_text)
                padding = column_widths[column] - visible

                if header:
                    cell_text = term.bold(cell_text)

                if numeric[column]:
                    cell_text = f'{" " * padding}{cell_text}'
                else:
                    cell_text = f'{cell_text}{" " * padding}'

                cell_texts.append(cell_text)

            rendered.append(f'{term.grey("│")} {" │ ".join(cell_texts)} {term.grey("│")}')

        return rendered

    def _apply_inline(self, text: str) -> str:
        unescaped = self._INLINE_ESCAPE_PATTERN.sub(r'\1', text)
        return self._INLINE_PATTERN.sub(self._style_inline, unescaped)

    def _style_inline(self, match: re.Match[str]) -> str:
        name, value = next(
            (name, value) for name, value in match.groupdict().items() if value is not None
        )

        if name == 'code':
            styled = self.term.yellow(value[1:-1])
        elif name == 'bold':
            styled = self.term.bold(value[2:-2])
        elif name == 'strike':
            styled = self.term.strikethrough(value[2:-2])
        elif name == 'italic':
            styled = self.term.italic(value[1:-1])
        elif name == 'link':
            label, url = value[1:-1].split('](', 1)
            styled = self._styled_link(label, url.rstrip(')'))
        elif name == 'image':
            alt = value[2:-1].split('](', 1)[0]
            styled = self.term.reverse(alt or 'image')
        elif name == 'html':
            styled = self._HTML_TAGS.get(value, '')
        else:
            styled = value

        return styled

    def _styled_link(self, label: str, url: str) -> str:
        term = self.term

        if not url or url.startswith('#') or url == label:
            return term.underline(label)

        return f'{term.underline(label)} {term.dim(url)}'

    @staticmethod
    def _bullet_for(marker: str) -> str:
        return {'-': '•', '*': '•', '+': '◦'}.get(marker, '•')
