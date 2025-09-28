from dandy import Decoder


class AnimalFamilyDecoder(Decoder):
    mapping_keys_description = "Animal Sounds"
    mapping = {
        "barking": "dog",
        "meowing": "cat",
        "quacking": "duck"
    }


animal_families = AnimalFamilyDecoder().process(
    "I was out on a walk and heard some barking",
    max_return_values=1
)

# Output: dog