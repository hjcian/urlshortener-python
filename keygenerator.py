import hashlib
import string

CHARSET = string.digits + string.ascii_uppercase + string.ascii_lowercase
BASE62 = len(CHARSET)

TOKEN_LENGTH = 6
# TOKEN_LENGTH is pre-computed during system design phase, 6 letters can
# accommodate around 15 billions URLs

BYTE = 8  # 8 bits


def getInterger(url):
    byte_array = hashlib.md5(url.encode()).digest()

    big_num = sum([
        byte_array[i] << ((len(byte_array) - i - 1) * BYTE)
        for i in range(len(byte_array))
    ])

    return big_num


def encode(big_num):
    token = ""

    while big_num > 0:
        big_num, x = divmod(big_num, BASE62)
        token = "{}{}".format(CHARSET[x], token)

    return token


def generate(url):
    big_num = getInterger(url)
    token = encode(big_num)
    token = token[:TOKEN_LENGTH]
    return token


if __name__ == "__main__":
    import random

    num = getInterger("{}".format(random.random()))
    token = encode(num)

    print(num)
    print(token)
    print(token[:TOKEN_LENGTH])
