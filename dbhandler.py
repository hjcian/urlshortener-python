from pymongo import MongoClient
from redis import Redis

from logger import LOGGER


def createMongoClient(db_host, db_post, database, collection):
    url = 'mongodb://{}:{}/'.format(db_host, db_post)
    client = MongoClient(url)
    db = client[database]
    collection = db[collection]
    return collection


def createRedisClient(cache_host, cache_port):
    r = Redis(host=cache_host, port=cache_port)
    return r


class _db(object):
    def update(self, url, token):
        raise NotImplementedError()

    def get(self, token):
        raise NotImplementedError()

    def check(self, token):
        raise NotImplementedError()


class InMemoryKV(_db):
    def __init__(self):
        self.db = {}

    def update(self, url, token):
        self.db[token] = url

    def get(self, token):
        return self.db.get(token)

    def check(self, token):
        return token in self.db


class MongoDB(_db):
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


class RedisCache(_db):
    def __init__(self, cache_host, cache_port, db_instance):
        self.cache = createRedisClient(cache_host, cache_port)
        self.db = db_instance

    def update(self, url, token):
        # just use db's update
        return self.db.update(url, token)

    def get(self, token):
        url = self.cache.get(token)
        if url:  # cache hit
            LOGGER.debug("[{}] cache HIT: {}".format(
                self.__class__.__name__, token))
            return url.decode()  # python 3 is a byte object

        LOGGER.debug("[{}] cache MISS: {}".format(
            self.__class__.__name__, token))
        url = self.db.get(token)

        if url:  # app is responsible for update cache
            self.cache.set(token, url)
            LOGGER.debug("[{}] update cache: {}:{}".format(
                self.__class__.__name__, token, url))

        return url

    def check(self, token):
        url = self.cache.get(token)
        if url:  # cache hit
            return True

        url = self.db.get(token)
        return bool(url)


def createDB(mode, db_host=None, db_port=None,
             cache_host=None, cache_port=None):
    """
    Return:
        A DB object inherited from _db
    """
    if mode not in ("memory", "mongodb", "cachedb"):
        raise RuntimeError("DBMODE={} is not supported".format(mode))
    LOGGER.info("DB mode: {}".format(mode))

    db = None
    if mode == "memory":
        db = InMemoryKV()
    elif mode == "mongodb":
        db = MongoDB(db_host, db_port, "urlshortener", "url")
    elif mode == "cachedb":
        mongo = MongoDB(db_host, db_port, "urlshortener", "url")
        db = RedisCache(cache_host, cache_port, mongo)

    return db


class DBHandler(object):
    INSERT_OK = 0

    def __init__(self, db):
        self.db = db

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
