from dandy import BaseIntel, Bot

class ClownIntel(BaseIntel):
    clown_name: str
    can_juggle: bool
    real_name: str | None = None

bozo = ClownIntel(
    clown_name='Bozo',
    can_juggle=True
)

print(bozo.can_juggle)

# True

class FakeClownBot(Bot):
    def process(self, clown_description: str) -> ClownIntel:
        return self.llm.prompt_to_intel(
            prompt=clown_description,
            intel_class=ClownIntel,
            exclude_fields={'real_name'},
        )


another_clown = FakeClownBot().process(
    clown_description='I am a big fan of juggling, can you please create me a clown!',
)

print(another_clown)

# Output: clown_name='Bouncing Buddy' can_juggle=True real_name=None