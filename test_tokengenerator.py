import unittest

from tokengenerator import encode, generate


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

    def test_generate_invalid_urls(self):
        invalid_urls = [
            "http://examplecom",
            "http//example.com",
            "httpssss://example.com",
            "htt://example.com",
        ]
        for invalid_url in invalid_urls:
            token = generate(invalid_url, 6)
            self.assertEqual(token, None)
