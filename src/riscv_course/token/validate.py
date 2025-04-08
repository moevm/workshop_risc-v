# Код для размещения на stepik

import zlib
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
from datetime import datetime, timezone
import random

TASK="lab1_asm_intro" # Название задачи
SEED="1111" # Seed
VALID_STRING=TASK + "_" + SEED
TOKEN_LIFE_TIME_SECONDS=200 # Время жизни токена в секундах 

def generate_answer_token(keyword: str) -> str:
    """
    Generates a token containing the ``keyword`` and the current time stamp inside it
    :param keyword: The string that will be encoded in the token
    :return: Answer token
    """
    keyword = keyword.encode()
    c = datetime.now(timezone.utc)
    for i in range(random.randint(5, 15)):
        ins = random.randint(0, len(keyword) - 1)
        keyword = keyword[:ins] + b':' + keyword[ins:]
    postfix = ":" + str(c.timestamp())
    keyword = keyword + postfix.encode()
    return b64e(zlib.compress(keyword, 9)).decode()


def validate_answer_token(token: str, keyword: str, seconds_delta: int) -> bool:
    """
    Paired to the generate_answer_token() function.
        1. Checks ``token`` to see if ``keyword`` has been encoded in it.
        2. Also checks that the ``token`` was generated at least ``seconds_delta`` seconds ago
    :param keyword: The string that should be encoded in the token
    :param token: Encoded string
    :param seconds_delta: Token lifetime
    :return: ``True`` if both conditions are met, ``False`` otherwise
    """
    unobscured = zlib.decompress(b64d(token.encode())).decode()
    split_ind = unobscured.rfind(':')
    if split_ind == -1:
        return False
    c = datetime.fromtimestamp(float(unobscured[split_ind + 1:]), timezone.utc)
    c_now = datetime.now(timezone.utc)
    diff = c_now - c
    if diff.seconds > seconds_delta:
        return False
    unobscured = unobscured[:split_ind].replace(':', '')
    if unobscured != keyword:
        return False
    return True


def check(reply):
    return validate_answer_token(reply, VALID_STRING, TOKEN_LIFE_TIME_SECONDS)    


def solve():
    return generate_answer_token(VALID_STRING)
