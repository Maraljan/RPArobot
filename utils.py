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


def parse_uii_from_text(text: str) -> str:
    uii = text[1].split('Unique Investment Identifier (UII): ')[1].split('Section B')[0]
    return uii


def parse_name_investment_from_text(text: str) -> str:
    name_investment = text[1].split('Name of this Investment: ')[1].split('2.')[0].replace('\n', ' ')
    return name_investment
