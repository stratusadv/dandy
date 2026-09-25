from dandy import Bot


class AnimalFamilyDecoder(Bot):
    def process(self, prompt: str) -> str:
        return self.llm.decoder.prompt_to_value(
            prompt=prompt,
            keys_description='book themes',
            keys_values={
                'barking': 'dog',
                'meowing': 'cat',
                'quacking': 'duck'
            },
        )


animal_families = AnimalFamilyDecoder().process('I was out on a walk and heard some barking')

# Output: dog