from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from dandy.application.agent.attachments import (
    ATTACHMENT_KIND_AUDIO,
    ATTACHMENT_KIND_IMAGE,
    ATTACHMENT_KIND_PROJECT_FILE,
    TurnAttachment,
    attachments_token_count,
    detect_attachment_paths,
    prepare_turn_attachments,
)
from dandy.domain.tokens.estimate import (
    TOKEN_COUNT_IMAGE_HIGH_DEFAULT,
    get_estimated_token_count_for_string,
)


def _write(path: Path, content: str = 'hello') -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


class TestDetectAttachmentPaths(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.base_path = Path(self.temp_directory_context.name)

    def tearDown(self) -> None:
        self.temp_directory_context.cleanup()

    def test_existing_relative_path_is_resolved_against_the_project_root(self) -> None:
        file_path = _write(self.base_path / 'notes' / 'draft.txt')

        remaining, paths = detect_attachment_paths(
            'summarize notes/draft.txt for me', self.base_path
        )

        self.assertEqual(paths, [file_path])
        self.assertEqual(remaining, 'summarize for me')

    def test_existing_absolute_path_is_used_verbatim(self) -> None:
        file_path = _write(self.base_path / 'report.pdf')

        remaining, paths = detect_attachment_paths(f'look at {file_path}', self.base_path)

        self.assertEqual(paths, [file_path])
        self.assertEqual(remaining, 'look at')

    def test_missing_paths_and_urls_are_ignored(self) -> None:
        remaining, paths = detect_attachment_paths(
            'see notes/missing.txt and https://example.com/page.png', self.base_path
        )

        self.assertEqual(paths, [])
        self.assertEqual(remaining, 'see notes/missing.txt and https://example.com/page.png')

    def test_prose_without_slashed_tokens_is_untouched(self) -> None:
        remaining, paths = detect_attachment_paths('fix the login bug', self.base_path)

        self.assertEqual(paths, [])
        self.assertEqual(remaining, 'fix the login bug')

    def test_multiple_paths_preserve_the_surrounding_text(self) -> None:
        first = _write(self.base_path / 'a.txt')
        second = _write(self.base_path / 'b' / 'c.md')

        remaining, paths = detect_attachment_paths(
            'diff a.txt against b/c.md and explain', self.base_path
        )

        self.assertEqual(paths, [first, second])
        self.assertIn('diff', remaining)
        self.assertIn('against', remaining)
        self.assertIn('and explain', remaining)

    def test_empty_text_returns_empty(self) -> None:
        remaining, paths = detect_attachment_paths('', self.base_path)

        self.assertEqual((remaining, paths), ('', []))


class TestPrepareTurnAttachments(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.base_path = Path(self.temp_directory_context.name)

    def tearDown(self) -> None:
        self.temp_directory_context.cleanup()

    def test_image_is_classified_and_left_in_place(self) -> None:
        image_path = _write(self.base_path / 'shot.png', 'png-bytes')

        attachments, issues = prepare_turn_attachments([image_path], self.base_path)

        self.assertEqual(issues, [])
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0].kind, ATTACHMENT_KIND_IMAGE)
        self.assertIsNone(attachments[0].delivery_path)

    def test_audio_is_classified_and_left_in_place(self) -> None:
        audio_path = _write(self.base_path / 'clip.mp3', 'mp3-bytes')

        attachments, issues = prepare_turn_attachments([audio_path], self.base_path)

        self.assertEqual(issues, [])
        self.assertEqual(attachments[0].kind, ATTACHMENT_KIND_AUDIO)

    def test_project_file_is_copied_into_the_dandy_directory(self) -> None:
        source_path = _write(self.base_path / 'data' / 'rows.csv', 'a,b\n1,2\n')

        attachments, issues = prepare_turn_attachments([source_path], self.base_path)

        self.assertEqual(issues, [])
        self.assertEqual(attachments[0].kind, ATTACHMENT_KIND_PROJECT_FILE)
        delivery_path = attachments[0].delivery_path
        self.assertIsNotNone(delivery_path)
        self.assertTrue(delivery_path.is_file())
        self.assertTrue(
            str(delivery_path).startswith(str(self.base_path / '.dandy' / 'attachments'))
        )
        self.assertEqual(delivery_path.read_text(), 'a,b\n1,2\n')
        self.assertIn('rows.csv', delivery_path.name)

    def test_project_file_name_collisions_get_a_counter(self) -> None:
        source_path = _write(self.base_path / 'rows.csv', 'v1')
        directory = self.base_path / '.dandy' / 'attachments'
        directory.mkdir(parents=True)
        (directory / '20260101T000000__rows.csv').write_text('old')

        attachments, issues = prepare_turn_attachments([source_path], self.base_path)

        self.assertEqual(issues, [])
        self.assertNotEqual(attachments[0].delivery_path.name, '20260101T000000__rows.csv')
        self.assertTrue(attachments[0].delivery_path.is_file())

    def test_an_unreadable_file_becomes_an_issue(self) -> None:
        missing = self.base_path / 'gone.txt'

        attachments, issues = prepare_turn_attachments([missing], self.base_path)

        self.assertEqual(attachments, [])
        self.assertEqual(len(issues), 1)
        self.assertIn('gone.txt', issues[0])


class TestAttachmentsTokenCount(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.base_path = Path(self.temp_directory_context.name)

    def tearDown(self) -> None:
        self.temp_directory_context.cleanup()

    def test_images_price_at_the_high_detail_default(self) -> None:
        image_path = _write(self.base_path / 'a.png', 'x')
        attachment = TurnAttachment(source_path=image_path, kind=ATTACHMENT_KIND_IMAGE)

        self.assertEqual(attachments_token_count([attachment]), TOKEN_COUNT_IMAGE_HIGH_DEFAULT)

    def test_audio_prices_on_its_base64_payload(self) -> None:
        audio_path = _write(self.base_path / 'a.mp3', 'mp3-bytes')
        attachment = TurnAttachment(source_path=audio_path, kind=ATTACHMENT_KIND_AUDIO)

        self.assertEqual(
            attachments_token_count([attachment]),
            get_estimated_token_count_for_string('bXAzLWJ5dGVz'),
        )

    def test_project_files_cost_nothing_in_the_token_budget(self) -> None:
        file_path = _write(self.base_path / 'a.txt', 'x')
        attachment = TurnAttachment(
            source_path=file_path, kind=ATTACHMENT_KIND_PROJECT_FILE, delivery_path=file_path
        )

        self.assertEqual(attachments_token_count([attachment]), 0)

    def test_no_attachments_cost_nothing(self) -> None:
        self.assertEqual(attachments_token_count([]), 0)
