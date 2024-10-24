from sys import argv
import zlib
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
from datetime import datetime, timezone
import random

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

if __name__ == '__main__':
    token = generate_answer_token(argv[1])
    print(token)


