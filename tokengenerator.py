import hashlib
import string

CHARSET = string.digits + string.ascii_uppercase + string.ascii_lowercase
BASE62 = len(CHARSET)

EIGHT_BITS = 8  # 1 byte = 8 bits


def getInterger(url):
    byte_array = hashlib.md5(url.encode()).digest()

    big_num = sum([
        byte_array[i] << ((len(byte_array) - i - 1) * EIGHT_BITS)
        for i in range(len(byte_array))
    ])

    return big_num


def encode(big_num):
    token = ""

    while big_num > 0:
        big_num, x = divmod(big_num, BASE62)
        token = "{}{}".format(CHARSET[x], token)

    return token


def validateURL(url):
    """
    Very simple validation
    """
    if (url.lower().startswith("http://")
            or url.lower().startswith("https://"))\
            and "." in url:
        return True
    return False


def generate(url, token_len=6):
    if not validateURL(url):
        return None

    big_num = getInterger(url)
    token = encode(big_num)
    token = token[:token_len]
    return token


if __name__ == "__main__":
    import random
    import json

    num = getInterger("{}".format(random.random()))
    token = encode(num)

    print(num)
    print(token)
    print(token[:TOKEN_LENGTH])
    urls = []
    tokens = []
    for i in range(100000):
        url = "http://{:x>10}.com".format(i)
        token = generate(url)
        urls.append(url)
        tokens.append(token)
        # print(url, token)

    json.dump({
        "urls": urls,
        "tokens": tokens
    }, open("data.json", "w"), indent=2)
