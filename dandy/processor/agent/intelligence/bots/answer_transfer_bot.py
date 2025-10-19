from pydantic.main import IncEx

from dandy import BaseIntel
from dandy.processor.bot.bot import Bot
from dandy.llm.prompt.prompt import Prompt


class AnswerTransferBot(Bot):
    llm_role = 'Answer Transfer Bot'
    llm_task = 'Fill out the actual result to this task using the answer provided.'
    llm_guidelines = Prompt().list(['This answer does not need to be validated.'])

    def process(
        self,
        answer_intel: BaseIntel,
        task_prompt: Prompt,
        task_intel: BaseIntel,
        include_fields: IncEx,
        exclude_fields: IncEx,
    ) -> BaseIntel:
        return self.llm.prompt_to_intel(
            prompt=(
                Prompt()
                .sub_heading('Task:')
                .prompt(task_prompt)
                .line_break()
                .sub_heading('Answer:')
                .intel(answer_intel)
            ),
            intel_object=task_intel,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
        )
