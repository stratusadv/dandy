from dandy.application.agent.intel import CompactionSummaryIntel
from dandy.application.agent.intelligence.prompts.compaction_prompt import compaction_prompt
from dandy.application.bot.bot import Bot
from dandy.domain.prompt.prompt import Prompt


class CompactionBot(Bot):
    role = 'Conversation Compaction Assistant'
    task = (
        'Summarize the earlier part of a coding conversation into a compact, '
        'structured summary that lets the work continue without the full transcript.'
    )

    def __post_init__(self) -> None:
        super().__post_init__()
        self.llm_config = 'DEFAULT'
        self.guidelines = self.build_guidelines()

    @staticmethod
    def build_guidelines() -> Prompt:
        return (
            Prompt()
            .sub_heading('Response Format')
            .list(
                [
                    (
                        'Respond with raw JSON only. Do not wrap the JSON in markdown '
                        'code fences and do not add any other text around it.'
                    ),
                    (
                        'Be concise: each list item is one short line, and the whole '
                        'summary stays under about 1500 words.'
                    ),
                ]
            )
        )

    def process(self, conversation_text: str) -> CompactionSummaryIntel:
        return self.llm.prompt_to_intel(
            prompt=compaction_prompt(conversation_text), intel_class=CompactionSummaryIntel
        )
