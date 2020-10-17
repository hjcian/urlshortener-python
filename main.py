from flask import Flask, request
import hashlib
import string

app = Flask(__name__)

CHARSET = string.digits + string.ascii_uppercase + string.ascii_lowercase
BASE = len(CHARSET)
CONSIDERED_BYTES = 5  # 40 bits of 128 bits (MD5)
BYTE = 8  # 8 bits

DB = {}


def getInterger(url, apikey):
    # "a" -> "xnddqK"
    byte_array = hashlib.md5((url + apikey).encode()).digest()

    big_num = sum([
        byte_array[i] << ((CONSIDERED_BYTES - i - 1) * BYTE)
        for i in range(CONSIDERED_BYTES)
    ])

    return big_num


def encode(big_num):
    token = ""

    while big_num > 0:
        big_num, x = divmod(big_num, BASE)
        token = "{}{}".format(CHARSET[x], token)

    return token


def generateToken(url, apikey):
    big_num = getInterger(url, apikey)
    token = encode(big_num)
    return token


@app.route('/shortenURL', methods=['POST'])
def shortenURL():
    req = request.get_json()
    url = req.get("url")
    apikey = req.get("apikey")

    token = generateToken(url, apikey)
    DB[token] = url
    return "{}, {}".format(apikey, token), 200


@app.route('/getURL', methods=['POST'])
def getURL():
    req = request.get_json()
    token = req.get("token")

    url = DB.get(token)
    return "{}: {}".format(token, url), 200


if __name__ == "__main__":
    app.run("0.0.0.0", port=12345, debug=True)
