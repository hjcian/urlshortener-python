import os
import json

from flask import Flask, Response, request
from flask_restful import Resource, Api
from flask_cors import CORS

from logger import LOGGER
from dbhandler import DBHandler, createDB
from tokengenerator import generate


TOKEN_LEN = os.environ.get("TOKEN_LEN", 5)
# TOKEN_LEN is pre-computed during system design phase
# 6 letters can accommodate around 15 billions URLs
# - 6 letters can produce 56 billions (56,800,235,584) requirements
# - 5 letters can produce 900 millions (916,132,832) requirements


class ShortenURL(Resource):
    def __init__(self, db):
        self.db = db

    def post(self):
        try:
            req = request.get_json()
            url = req.get("url")
            if not url or not isinstance(url, str):
                return Response(status=400)

            token = generate(url, TOKEN_LEN)
            if not token:
                # invalid URL
                return Response(status=400)

            ret = self.db.insertEntry(url=url, token=token)
            if ret != self.db.INSERT_OK:
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


class GetURL(Resource):
    def __init__(self, db):
        self.db = db

    def post(self):
        try:
            req = request.get_json()
            token = req.get("token")
            if not token or not isinstance(token, str):
                return Response(status=400)

            url = self.db.getURL(token)
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


class Redirects(Resource):
    def __init__(self, db):
        self.db = db

    def get(self, token):
        url = self.db.getURL(token)
        if not url:
            return Response(status=404)

        headers = {
            "location": url
        }
        return Response(
            status=302,
            headers=headers
        )


def set_resources(app, db):
    app.add_resource(ShortenURL, "/shortenURL",
                     resource_class_kwargs={'db': db})
    app.add_resource(GetURL, "/getURL",
                     resource_class_kwargs={'db': db})
    app.add_resource(Redirects, "/<token>",
                     resource_class_kwargs={'db': db})
    return app


def create_app(db):
    app = Flask(__name__)
    api = Api(app)
    CORS(app)
    set_resources(api, db)
    return app


def create_db():
    db = DBHandler(
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
    return db


if __name__ == "__main__":
    LOGGER.info("Server start...")
    db = create_db()
    app = create_app(db)
    app.run("0.0.0.0", port=12345, debug=True)
    LOGGER.info("Server shutdown...")
