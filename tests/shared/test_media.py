from unittest import TestCase

from dandy.shared.exceptions import FileRecoverableError
from dandy.shared.media import (
    get_audio_format_from_base64_string,
    get_audio_mime_type_from_base64_string,
    get_image_format_from_base64_string,
    get_image_mime_type_from_base64_string,
)


class TestMediaUtils(TestCase):
    def test_get_image_mime_type_from_base64_string(self) -> None:
        self.assertEqual(get_image_mime_type_from_base64_string('JVBERi0'), 'application/pdf')
        self.assertEqual(get_image_mime_type_from_base64_string('R0lGODdh'), 'image/gif')
        self.assertEqual(get_image_mime_type_from_base64_string('R0lGODlh'), 'image/gif')
        self.assertEqual(get_image_mime_type_from_base64_string('iVBORw0KGgo'), 'image/png')
        self.assertEqual(get_image_mime_type_from_base64_string('/9j/'), 'image/jpg')

        with self.assertRaises(FileRecoverableError):
            get_image_mime_type_from_base64_string('random nonsense')

    def test_get_audio_mime_type_from_base64_string(self) -> None:
        self.assertEqual(get_audio_mime_type_from_base64_string('SUQzAAB'), 'audio/mp3')
        self.assertEqual(get_audio_mime_type_from_base64_string('//OyLz'), 'audio/mp3')
        self.assertEqual(get_audio_mime_type_from_base64_string('T2dnUwA'), 'audio/ogg')
        self.assertEqual(get_audio_mime_type_from_base64_string('UklGRgQ'), 'audio/wav')
        self.assertEqual(get_audio_mime_type_from_base64_string('AAAAZGx'), 'audio/mp4')
        # The bare '//' signature is checked before '//O', so mp4 input starting
        # with '//O' resolves through the mp3 signature.
        self.assertEqual(get_audio_mime_type_from_base64_string('//OyL9'), 'audio/mp3')

        with self.assertRaises(FileRecoverableError):
            get_audio_mime_type_from_base64_string('random nonsense')

    def test_get_audio_format_from_base64_string(self) -> None:
        self.assertEqual(get_audio_format_from_base64_string('SUQzAAB'), 'mp3')
        self.assertEqual(get_audio_format_from_base64_string('T2dnUwA'), 'ogg')
        self.assertEqual(get_audio_format_from_base64_string('UklGRgQ'), 'wav')

    def test_get_image_format_from_base64_string(self) -> None:
        self.assertEqual(get_image_format_from_base64_string('iVBORw0KGgo'), 'png')
        self.assertEqual(get_image_format_from_base64_string('/9j/4AA'), 'jpg')
