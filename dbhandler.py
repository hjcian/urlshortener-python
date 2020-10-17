class DBHandler(object):
    INSERT_OK = 0

    def __init__(self):
        self.db = {}

    def insertEntry(self, url, token):
        if token in self.db:
            return None

        # mimic the actual INSERT manipulation
        self.db[token] = url

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
