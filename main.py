import os
import json

from flask import Flask, Response, request

from logger import LOGGER
from dbhandler import DBHandler, createDB
from tokengenerator import generate

app = Flask(__name__)
DB = DBHandler(
    createDB(
        mode=os.environ.get("DBMODE", "memory"),
        db_host=os.environ.get("DBHOST", "127.0.0.1"),
        db_port=os.environ.get("DBPORT", 27017),
        cache_host=os.environ.get("CACHEHOST", "127.0.0.1"),
        cache_port=os.environ.get("CACHEPORT", 6379),
    )
)
# DB is a DB handler, can be an actual DB server's connection pool
# by passing some configurations.

TOKEN_LEN = os.environ.get("TOKEN_LEN", 5)
# TOKEN_LEN is pre-computed during system design phase
# 6 letters can accommodate around 15 billions URLs
# - 6 letters can produce 56 billions (56,800,235,584) requirements
# - 5 letters can produce 900 millions (916,132,832) requirements


@app.route('/shortenURL', methods=['POST'])
def shortenURL():
    try:
        req = request.get_json()
        url = req.get("url")
        if not url or not isinstance(url, str):
            return Response(status=400)

        token = generate(url, TOKEN_LEN)
        if not token:
            # invalid URL
            return Response(status=400)

        ret = DB.insertEntry(url=url, token=token)
        if ret != DB.INSERT_OK:
            LOGGER.warning((
                "entry collision, "
                "but return the token for accessing is OK"))

        return Response(
            response=json.dumps({
                "token": token
            }),
            status=200,
            mimetype="application/json"
        )
    except Exception as e:
        LOGGER.error("Unexpected error: {}".format(e), exc_info=True)
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
        LOGGER.error("Unexpected error: {}".format(e), exc_info=True)
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
    LOGGER.info("Server start...")
    app.run("0.0.0.0", port=12345, debug=True)
    LOGGER.info("Server shutdown...")
