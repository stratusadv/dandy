import string
import random


def generate_new_debug_event_id() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(random.choices(alphabet, k=4))