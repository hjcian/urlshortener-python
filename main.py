import json

from flask import Flask, Response, request

from dbhandler import DBHandler
from tokengenerator import generate

app = Flask(__name__)
DB = DBHandler()
# DB is a DB handler, can be an actual DB server's connection pool
# by passing some configurations.


@app.route('/shortenURL', methods=['POST'])
def shortenURL():
    try:
        req = request.get_json()
        url = req.get("url")
        if not url or not isinstance(url, str):
            return Response(status=400)

        token = generate(url)
        ret = DB.insertEntry(url=url, token=token)
        if ret != DB.INSERT_OK:
            print("entry collision, but return the token for accessing is OK")

        return Response(
            response=json.dumps({
                "token": token
            }),
            status=200,
            mimetype="application/json"
        )
    except Exception as e:
        print("Unexpected error: {}".format(e))
        return Response(status=500)


@app.route('/getURL', methods=['POST'])
def getURL():
    try:
        req = request.get_json()
        token = req.get("token")
        if not token or not isinstance(token, str):
            return Response(status=400)

        url = DB.getURL(token)
        if not url:
            return Response(status=404)

        return Response(
            response=json.dumps({
                "url": url
            }),
            status=200,
            mimetype="application/json"
        )
    except Exception as e:
        print("Unexpected error: {}".format(e))
        return Response(status=500)


@app.route('/<token>', methods=['GET'])
def redirect(token):
    url = DB.getURL(token)
    if not url:
        return Response(status=404)

    headers = {
        "location": url
    }
    return Response(
        status=302,
        headers=headers
    )


if __name__ == "__main__":
    app.run("0.0.0.0", port=12345, debug=True)
