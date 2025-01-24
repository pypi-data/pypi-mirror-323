import random
import string
from time import time


def get_random_string(length: int) -> str:
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def get_random_id() -> str:
    # Timestamp (9 digits) + Random string (10 digits)
    return f'{time.time().strftime("%Y%m%d%H%M%S")}_{get_random_string(10)}'
