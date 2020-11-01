import unittest

from dbhandler import DBHandler, createDB


class TestDBHandler(unittest.TestCase):
    def setUp(self):
        self.db = DBHandler(createDB("memory"))

    def test_insertEntry(self):
        url = "aaaaa"
        token = "bbbbb"
        ret = self.db.insertEntry(url, token)
        self.assertEqual(ret, self.db.INSERT_OK)

        token = "ccccc"
        ret = self.db.insertEntry(url, token)
        self.assertEqual(ret, self.db.INSERT_OK)

    def test_getURL(self):
        url = "aaaaa"

        token = "bbbbb"
        ret = self.db.getURL(token)
        self.assertEqual(ret, None)

        self.db.insertEntry(url, token)
        ret = self.db.getURL(token)
        self.assertEqual(ret, url)
