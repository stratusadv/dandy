from dandy.application.agent.intel import SessionNameIntel
from dandy.application.agent.prompts import session_name_prompt
from dandy.application.bot.bot import Bot
from dandy.shared.settings.load import get_cli_llm_config
from dandy.domain.prompt.prompt import Prompt


class SessionNamingBot(Bot):
    role = 'Session Naming Assistant'

    def __post_init__(self) -> None:
        super().__post_init__()
        self.llm_config = get_cli_llm_config('SIMPLE')
        self.guidelines = self.build_guidelines()

    def build_guidelines(self) -> Prompt:
        return (
            Prompt()
            .sub_heading('Response Format')
            .list(
                [
                    (
                        'Respond with raw JSON only. Do not wrap the JSON in '
                        'markdown code fences and do not add any other text '
                        'around it.'
                    )
                ]
            )
        )

    task = (
        'Create a short title for the user\'s coding request: 8 to 10 words, '
        'title case, plain words only.'
    )

    def process(self, request_text: Prompt | str) -> SessionNameIntel:
        prompt = request_text.to_str() if isinstance(request_text, Prompt) else request_text
        return self.llm.prompt_to_intel(
            prompt=session_name_prompt(prompt), intel_class=SessionNameIntel
        )
