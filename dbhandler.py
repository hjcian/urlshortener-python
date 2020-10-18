from pymongo import MongoClient
from logger import LOGGER


def createMongoClient(db_host, db_post, database, collection):
    url = 'mongodb://{}:{}/'.format(db_host, db_post)
    client = MongoClient(url)
    db = client[database]
    collection = db[collection]
    return collection


class InMemoryKV(object):
    def __init__(self):
        self.db = {}

    def update(self, url, token):
        self.db[token] = url

    def get(self, token):
        return self.db.get(token)

    def check(self, token):
        return token in self.db


class MongoDB(object):
    def __init__(self, db_host, db_post, database, collection):
        self.db = createMongoClient(db_host, db_post, database, collection)
        if "token_index" not in self.db.index_information():
            resp = self.db.create_index(
                "token", name="token_index", unique=True)
            LOGGER.info("[{}] create index: {}".format(
                self.__class__.__name__, resp))

    def update(self, url, token):
        ret = self.db.insert_one(
            {
                "token": token,
                "url": url,
            }
        )
        LOGGER.info("[{}] insert id: {}".format(
            self.__class__.__name__, ret.inserted_id))

    def get(self, token):
        ret = self.db.find_one(
            filter={
                "token": token
            },
            projection={
                "_id": False,
                "url": True
            }
        )
        return ret and ret.get("url")

    def check(self, token):
        return bool(self.get(token))


class DBHandler(object):
    INSERT_OK = 0

    def __init__(self, mode="memory", db_host=None, db_port=None):
        LOGGER.info("[{}] DB mode: {}".format(self.__class__.__name__, mode))
        if mode == "memory":
            self.db = InMemoryKV()
        elif mode == "mongodb":
            self.db = MongoDB(db_host, db_port, "urlshortener", "url")
        else:
            raise RuntimeError("DBMODE={} is not supported".format(mode))

    def insertEntry(self, url, token):
        if self.db.check(token):
            return None

        # mimic the actual INSERT manipulation
        self.db.update(url, token)

        return self.INSERT_OK

    def getURL(self, token):
        """
        Return:
            url (str): return 'string' if found mapping,
                        instead return 'None' means not found mapping
        """

        # mimic the actual SELECT manipulation
        url = self.db.get(token)

        return url
