import json

from flask import Flask, Response, request

from dbhandler import DBHandler
from keygenerator import generate

app = Flask(__name__)
DB = DBHandler()
# DB is a DB handler, can be an actual DB server's connection pool
# by passing some configurations.


@app.route('/shortenURL', methods=['POST'])
def shortenURL():
    req = request.get_json()
    url = req.get("url")

    token = generate(url)
    ret = DB.insertEntry(url=url, token=token)
    if ret != DB.INSERT_OK:
        print("entry collision, but return the token for accessing is OK")

    return Response(
        response=json.dumps({
            "url": url,
            "token": token
        }),
        status=200,
        mimetype="application/json"
    )


@app.route('/getURL', methods=['POST'])
def getURL():
    req = request.get_json()
    token = req.get("token")

    url = DB.getURL(token)
    if not url:
        return Response(status=404)

    return Response(
        response=json.dumps({
            "url": url,
            "token": token
        }),
        status=200,
        mimetype="application/json"
    )


if __name__ == "__main__":
    app.run("0.0.0.0", port=12345, debug=True)
