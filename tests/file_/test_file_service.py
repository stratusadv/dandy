from __future__ import annotations

import tempfile
from pathlib import Path
from unittest import TestCase


from dandy.core.exceptions import DandyCriticalError
from dandy.file.service import FileService


class TestFileService(TestCase):
    def setUp(self):
        self.file_service = FileService()
        self.tmpdir_ctx = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self.tmpdir_ctx.name)

    def tearDown(self):
        self.tmpdir_ctx.cleanup()

    def test_write_creates_parent_dir_and_writes_string(self):
        target = self.tmpdir / "nested" / "dir" / "file.txt"

        content = "hello world"
        self.file_service.write(target, content)

        self.assertTrue(target.exists(), "Expected file to be created")
        read_back = self.file_service.read(target)
        self.assertEqual(read_back, content)

    def test_append_appends_and_creates_if_missing(self):
        target = self.tmpdir / 'append' / 'data.log'

        self.file_service.append(target, 'one')
        self.assertTrue(target.exists())
        self.assertEqual(self.file_service.read(target), 'one')

        self.file_service.append(target, 'two')
        self.assertEqual(self.file_service.read(target), 'onetwo')

    def test_exists_and_remove_rm(self):
        target = self.tmpdir / "x" / "y" / "z.txt"
        self.assertFalse(self.file_service.exists(target))

        self.file_service.write(target, "data")
        self.assertTrue(self.file_service.exists(target))

        FileService.remove(target)
        self.assertFalse(self.file_service.exists(target))

        self.file_service.write(target, "data")
        self.assertTrue(self.file_service.exists(target))
        self.file_service.rm(target)
        self.assertFalse(self.file_service.exists(target))

    def test_make_directory_and_mkdir_idempotent(self):
        d = self.tmpdir / "a" / "b" / "c"
        self.assertFalse(d.exists())
        FileService.make_directory(d)
        self.assertTrue(d.exists())

        self.file_service.mkdir(d)
        self.assertTrue(d.exists())

    def test_read_raises_for_missing_file(self):
        missing = self.tmpdir / "nope" / "missing.txt"
        with self.assertRaises(DandyCriticalError):
            FileService.read(missing)

    def test_reset_callable(self):
        self.file_service.reset_service()
