import base64
import tempfile
from pathlib import Path
from unittest import TestCase

from dandy.shared.files import (
    append_to_file,
    clean_file_extensions,
    encode_file_to_base64,
    file_exists,
    get_directory_listing,
    get_directory_path_or_exception,
    get_file_extension_from_url_string,
    get_file_path_or_exception,
    make_directory,
    read_from_file,
    remove_directory,
    remove_file,
    write_to_file,
)
from dandy.shared.exceptions import FileCriticalError


class TestFiles(TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self._temp_dir.name)

    def tearDown(self) -> None:
        self._temp_dir.cleanup()

    def test_get_file_path_or_exception_returns_existing_path(self) -> None:
        file_path = self.temp_path / 'exists.txt'
        file_path.write_text('content', encoding='utf-8')

        self.assertEqual(get_file_path_or_exception(file_path), file_path)

    def test_get_file_path_or_exception_missing_path_raises(self) -> None:
        with self.assertRaises(FileCriticalError):
            get_file_path_or_exception('this/path/doesnt/exist')

    def test_get_directory_path_or_exception_returns_existing_path(self) -> None:
        self.assertEqual(get_directory_path_or_exception(self.temp_path), self.temp_path)

    def test_get_directory_path_or_exception_missing_path_raises(self) -> None:
        with self.assertRaises(FileCriticalError):
            get_directory_path_or_exception('this/dir/doesnt/exist')

    def test_file_exists(self) -> None:
        file_path = self.temp_path / 'exists.txt'
        file_path.write_text('content', encoding='utf-8')

        self.assertTrue(file_exists(file_path))
        self.assertFalse(file_exists(self.temp_path / 'missing.txt'))

    def test_write_and_read_from_file(self) -> None:
        file_path = self.temp_path / 'nested' / 'directory' / 'file.txt'
        write_to_file(file_path, 'hello')

        self.assertEqual(read_from_file(file_path), 'hello')

    def test_read_from_file_missing_raises(self) -> None:
        with self.assertRaises(FileCriticalError):
            read_from_file(self.temp_path / 'missing.txt')

    def test_append_to_file_creates_when_missing(self) -> None:
        file_path = self.temp_path / 'appended.txt'
        append_to_file(file_path, 'first')
        append_to_file(file_path, 'second')

        self.assertEqual(read_from_file(file_path), 'firstsecond')

    def test_remove_file(self) -> None:
        file_path = self.temp_path / 'to_remove.txt'
        file_path.write_text('content', encoding='utf-8')

        remove_file(file_path)

        self.assertFalse(file_exists(file_path))

    def test_remove_file_missing_is_no_op(self) -> None:
        remove_file(self.temp_path / 'never_existed.txt')

        self.assertFalse(file_exists(self.temp_path / 'never_existed.txt'))

    def test_make_directory(self) -> None:
        directory_path = self.temp_path / 'a' / 'b' / 'c'

        make_directory(directory_path)

        self.assertTrue(directory_path.is_dir())

    def test_remove_directory(self) -> None:
        directory_path = self.temp_path / 'to_remove'
        directory_path.mkdir()

        remove_directory(directory_path)

        self.assertFalse(directory_path.exists())

    def test_clean_file_extensions(self) -> None:
        self.assertEqual(clean_file_extensions(['.py', 'md', 'txt']), ['.py', '.md', '.txt'])

    def test_encode_file_to_base64(self) -> None:
        file_path = self.temp_path / 'binary.bin'
        content = b'\x00\x01\x02hello'
        file_path.write_bytes(content)

        self.assertEqual(
            encode_file_to_base64(file_path), base64.b64encode(content).decode('utf-8')
        )

    def test_encode_file_to_base64_missing_raises(self) -> None:
        with self.assertRaises(FileCriticalError):
            encode_file_to_base64(self.temp_path / 'missing.bin')

    def test_get_directory_listing(self) -> None:
        (self.temp_path / 'one.txt').write_text('1', encoding='utf-8')
        (self.temp_path / 'two.py').write_text('2', encoding='utf-8')
        nested_dir = self.temp_path / 'nested'
        nested_dir.mkdir()
        (nested_dir / 'three.txt').write_text('3', encoding='utf-8')
        (nested_dir / 'deep').mkdir()
        (nested_dir / 'deep' / 'four.txt').write_text('4', encoding='utf-8')

        listing = get_directory_listing(self.temp_path)
        self.assertIn(str(self.temp_path / 'one.txt'), listing)
        self.assertIn(str(self.temp_path / 'nested' / 'three.txt'), listing)
        self.assertIn(str(self.temp_path / 'nested' / 'deep' / 'four.txt'), listing)

        shallow_listing = get_directory_listing(self.temp_path, max_depth=1)
        self.assertIn(str(self.temp_path / 'nested' / 'three.txt'), shallow_listing)
        self.assertNotIn(str(self.temp_path / 'nested' / 'deep' / 'four.txt'), shallow_listing)

        filtered_listing = get_directory_listing(self.temp_path, file_extensions=['.txt'])
        self.assertIn(str(self.temp_path / 'one.txt'), filtered_listing)
        self.assertNotIn(str(self.temp_path / 'two.py'), filtered_listing)

    def test_get_file_extension_from_url_string(self) -> None:
        self.assertEqual(get_file_extension_from_url_string('https://example.com/a/b.pdf'), 'pdf')
        self.assertEqual(get_file_extension_from_url_string('https://example.com/plain'), '')
