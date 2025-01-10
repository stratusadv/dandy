from random import randint

def generate_random_seed() -> int:
    return randint(0, 2**63 - 1)