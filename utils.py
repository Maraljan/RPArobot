import time
import string
import datetime
from typing import Callable


def get_number_entries(text: str) -> int:
    text = text.split(' of ')[-1].strip(' entries')
    return int(text)


def wait_for_condition(expression: Callable[[], bool], timeout: datetime.timedelta):
    start = datetime.datetime.now()
    while not expression():
        now = datetime.datetime.now()
        if now - start >= timeout:
            raise TimeoutError
        time.sleep(1)


def index2col_name(idx: int) -> str:
    return string.ascii_uppercase[idx]
