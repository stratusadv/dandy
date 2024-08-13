from dandy.llm.prompt import Prompt


def test_prompt() -> Prompt:
    prompt = Prompt()
    prompt.text('Write me an amazing and original poem about traveling to Misty Mountains full of horses.')
    return prompt