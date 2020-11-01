import unittest

from tokengenerator import generate, encode


class TestTokenGenerator(unittest.TestCase):
    def test_encode(self):
        testCases = [
            (1, "1"),
            (62, "10")
        ]
        for test in testCases:
            self.assertEqual(encode(test[0]), test[1])

    def test_generate(self):
        url = "http://example.com"

        token = generate(url, 6)
        self.assertEqual(token, "5AGfzw")

        token = generate(url, 5)
        self.assertEqual(token, "5AGfz")
