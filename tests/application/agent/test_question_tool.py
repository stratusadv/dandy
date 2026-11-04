from unittest import TestCase

from dandy.application.agent.tools.question import QuestionTool


class TestQuestionToolSchema(TestCase):
    def test_schema_requires_question_and_allows_optional_string_choices(self) -> None:
        function = QuestionTool().to_function_dict()['function']

        self.assertEqual(function['name'], 'question')

        parameters = function['parameters']

        self.assertEqual(parameters['required'], ['question'])
        self.assertEqual(
            parameters['properties']['question'], {'title': 'Question', 'type': 'string'}
        )
        self.assertEqual(
            parameters['properties']['choices'],
            {
                'anyOf': [{'items': {'type': 'string'}, 'type': 'array'}, {'type': 'null'}],
                'default': None,
                'title': 'Choices',
            },
        )


class TestQuestionToolHandle(TestCase):
    def test_handle_without_ask_user_says_no_user_is_available(self) -> None:
        self.assertEqual(QuestionTool().handle('Which color?'), QuestionTool.NO_USER_ANSWER)

    def test_handle_returns_the_answer_from_the_injected_ask_user(self) -> None:
        seen: list[tuple[str, list[str]]] = []

        def ask_user(question: str, choices: list[str]) -> str:
            seen.append((question, choices))
            return 'blue'

        tool = QuestionTool(ask_user=ask_user)

        self.assertEqual(tool.handle('Which color?', ['red', 'blue']), 'blue')
        self.assertEqual(seen, [('Which color?', ['red', 'blue'])])

    def test_handle_normalizes_missing_choices_to_an_empty_list(self) -> None:
        seen: list[tuple[str, list[str]]] = []

        def ask_user(question: str, choices: list[str]) -> str:
            seen.append((question, choices))
            return 'free text'

        tool = QuestionTool(ask_user=ask_user)

        self.assertEqual(tool.handle('What should I call it?'), 'free text')
        self.assertEqual(seen, [('What should I call it?', [])])

    def test_question_tool_does_not_emit_a_story_beat(self) -> None:
        self.assertFalse(QuestionTool.emits_story_beat)
