from pathlib import Path, PurePosixPath
from unittest import TestCase

from dandy.domain.intel.intel import BaseIntel
from dandy.domain.message.message import Message, MessageHistory
from dandy.domain.request.options import LlmOptions
from dandy.domain.request.request import LlmRequestBody
from dandy.domain.skill.skill import BaseSkill
from dandy.domain.tool.tool import BaseTool
from dandy.infrastructure.llm.config import LlmConfig
from dandy.shared.hashing import HASH_LENGTH, HashMixin, canonicalize


class _LocationIntel(BaseIntel):
    location: str = 'nowhere'


class _EchoTool(BaseTool):
    name = 'echo'
    description = 'echoes'

    def handle(self, text: str = '') -> str:
        return text


class _ShoutTool(BaseTool):
    name = 'shout'
    description = 'shouts'

    def handle(self, text: str = '') -> str:
        return text


class _GitSkill(BaseSkill):
    name = 'git'
    description = 'git ops'
    prompt = 'be careful'
    active = False
    tools = ['status']

    def status(self) -> str:
        return 'ok'


class _PlainStateful(HashMixin):
    def __init__(self, label: str, count: int) -> None:
        self.label = label
        self.count = count


class TestHashMixin(TestCase):
    def test_equal_state_shares_both_levels(self) -> None:
        first = _LocationIntel(location='Paris')
        second = _LocationIntel(location='Paris')

        self.assertEqual(first.deep_hash(), second.deep_hash())
        self.assertEqual(first.shallow_hash(), second.shallow_hash())
        self.assertEqual(hash(first), hash(second))
        self.assertEqual(len(first.deep_hash()), HASH_LENGTH)

    def test_changed_state_changes_deep_hash(self) -> None:
        original = _LocationIntel(location='Paris')
        changed = _LocationIntel(location='Paris')
        changed.location = 'Lyon'

        self.assertNotEqual(changed.deep_hash(), original.deep_hash())

    def test_whitespace_drift_does_not_change_deep_hash(self) -> None:
        spaced = Message(role='user', content=[{'type': 'text', 'text': 'hello   world'}])
        folded = Message(role='user', content=[{'type': 'text', 'text': 'hello world'}])

        self.assertEqual(spaced.deep_hash(), folded.deep_hash())
        self.assertEqual(spaced.shallow_hash(), folded.shallow_hash())

    def test_messages_of_different_content_types_do_not_collide(self) -> None:
        text_message = Message(role='user', content=[{'type': 'text', 'text': ''}])
        image_message = Message(
            role='user',
            content=[{'type': 'image_url', 'image_url': {'url': 'x', 'detail': 'auto'}}],
        )
        empty_tool_message = Message(
            role='tool', tool_call_id='c1', content=[{'type': 'text', 'text': ''}]
        )

        hashes = {
            message.deep_hash() for message in (text_message, image_message, empty_tool_message)
        }

        self.assertEqual(len(hashes), 3)

    def test_shallow_level_folds_long_strings(self) -> None:
        shared_head = 'A' * 32
        shared_tail = 'Z' * 32
        first = _LocationIntel(location=shared_head + 'x' * 200 + shared_tail)
        second = _LocationIntel(location=shared_head + 'y' * 200 + shared_tail)

        self.assertEqual(first.shallow_hash(), second.shallow_hash())
        self.assertNotEqual(first.deep_hash(), second.deep_hash())

    def test_request_body_hash_tracks_model_and_history(self) -> None:
        history = MessageHistory(
            messages=[Message(role='user', content=[{'type': 'text', 'text': 'hi'}])]
        )
        first = LlmRequestBody(model='stratus.turbo', messages=history)
        second = LlmRequestBody(model='stratus.turbo', messages=MessageHistory())
        second.messages = MessageHistory(
            messages=[Message(role='user', content=[{'type': 'text', 'text': 'hi'}])]
        )

        self.assertEqual(first.deep_hash(), second.deep_hash())
        self.assertNotEqual(
            first.deep_hash(), LlmRequestBody(model='other', messages=first.messages).deep_hash()
        )

    def test_options_hash_tracks_values(self) -> None:
        self.assertEqual(
            LlmOptions(temperature=0.5).deep_hash(), LlmOptions(temperature=0.5).deep_hash()
        )
        self.assertNotEqual(
            LlmOptions(temperature=0.5).deep_hash(), LlmOptions(temperature=0.6).deep_hash()
        )

    def test_history_hash_changes_as_messages_are_added(self) -> None:
        history = MessageHistory(
            messages=[Message(role='user', content=[{'type': 'text', 'text': 'hi'}])]
        )
        before = history.deep_hash()

        history.add_message(role='assistant', text='reply')

        self.assertNotEqual(history.deep_hash(), before)

    def test_tool_hash_tracks_identity_attributes(self) -> None:
        self.assertEqual(_EchoTool().deep_hash(), _EchoTool().deep_hash())
        self.assertNotEqual(_EchoTool().deep_hash(), _ShoutTool().deep_hash())

    def test_skill_hash_tracks_active_override(self) -> None:
        self.assertEqual(_GitSkill().deep_hash(), _GitSkill().deep_hash())
        self.assertNotEqual(_GitSkill().deep_hash(), _GitSkill(active=True).deep_hash())

    def test_config_hash_tracks_resolved_endpoint(self) -> None:
        self.assertEqual(LlmConfig('DEFAULT').deep_hash(), LlmConfig('DEFAULT').deep_hash())

        config = LlmConfig('DEFAULT')
        config.model = 'another-model'

        self.assertNotEqual(config.deep_hash(), LlmConfig('DEFAULT').deep_hash())

    def test_plain_class_hash_uses_instance_state(self) -> None:
        self.assertEqual(_PlainStateful('a', 1).deep_hash(), _PlainStateful('a', 1).deep_hash())
        self.assertNotEqual(_PlainStateful('a', 1).deep_hash(), _PlainStateful('b', 1).deep_hash())

    def test_hashable_framework_objects_are_keyable(self) -> None:
        keyable = [
            Message(role='user', content=[{'type': 'text', 'text': 'hi'}]),
            MessageHistory(),
            _LocationIntel(location='Paris'),
            LlmOptions(temperature=0.5),
            LlmRequestBody(model='stratus.turbo'),
            _EchoTool(),
            _GitSkill(),
            LlmConfig('DEFAULT'),
        ]

        for keyable_object in keyable:
            self.assertIsInstance(hash(keyable_object), int)


class TestCanonicalize(TestCase):
    def test_dict_key_order_does_not_matter(self) -> None:
        self.assertEqual(canonicalize({'a': 1, 'b': 2}), canonicalize({'b': 2, 'a': 1}))

    def test_set_order_does_not_matter(self) -> None:
        self.assertEqual(
            canonicalize({'values': {'z', 'y', 'x'}}), canonicalize({'values': {'x', 'z', 'y'}})
        )

    def test_paths_reduce_to_strings(self) -> None:
        self.assertEqual(canonicalize(Path('/x/y')), canonicalize(PurePosixPath('/x/y')))

    def test_long_strings_fold_only_in_shallow_level(self) -> None:
        folded = canonicalize('word ' * 100, shallow=True)
        kept = canonicalize('word ' * 100, shallow=False)

        self.assertNotEqual(folded, kept)
        self.assertIn('...', folded)
        self.assertEqual(kept, ' '.join(('word ' * 100).split()))

    def test_whitespace_folds_in_both_levels(self) -> None:
        self.assertEqual(canonicalize('a  b\n c'), canonicalize('a b c'))

    def test_nested_models_reduce_to_their_digest(self) -> None:
        message = Message(role='user', content=[{'type': 'text', 'text': 'hi'}])
        canonical_message = canonicalize(message)

        self.assertEqual(canonical_message['__qualname__'], 'Message')
        self.assertEqual(canonical_message['__digest__'], message.deep_hash())
