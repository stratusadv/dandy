from dandy import BaseIntel, Bot, Prompt


class CandyIntel(BaseIntel):
    short_name: str
    long_name: str
    description: str


class CandyDesignBot(Bot):
    llm_config = 'LLAMA_3_2_3B'
    instructions_prompt = (
        Prompt()
        .text('You are a candy design bot and will be given a request to make a new type of candy.')
        .line_break()
        .heading('Rules')
        .list([
            'Make sure you response is sugar based not chocolate based.',
            'Do not include any chocolate based words or phrases in the response.',
            'Incorporate the theme of the request into the response.',
        ])
    )
    intel_class = CandyIntel

    def process(self, user_prompt: Prompt | str, candy_theme: str) -> CandyIntel:
        prompt = (
            Prompt()
            .heading('Request')
            .prompt(user_prompt)
            .line_break()
            .heading('Theme')
            .prompt(candy_theme)
        )

        return self.llm.prompt_to_intel(
            prompt=prompt,
        )


candy_intel = CandyDesignBot().process(
    user_prompt='Strawberries and Cookie Dough',
    candy_theme='Medieval Times'
)

print(candy_intel.short_name)

# Output: Cinnamon Lances