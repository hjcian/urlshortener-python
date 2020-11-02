import unittest

from main import create_app, create_db


class TestIntegrations(unittest.TestCase):
    def setUp(self):
        db = create_db()
        app = create_app(db)
        self.app = app.test_client()

    def test_shorten_and_get_and_redirect(self):
        url = "http://example.com"
        expected_token = "5AGfz"

        resp = self.app.post("/shortenURL", json={"url": url})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers["Content-Type"], "application/json")
        respj = resp.get_json()
        self.assertIn("token", respj)
        self.assertEqual(respj["token"], expected_token)

        resp = self.app.post("/getURL", json={"token": expected_token})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers["Content-Type"], "application/json")
        respj = resp.get_json()
        self.assertIn("url", respj)
        self.assertEqual(respj["url"], url)

        resp = self.app.get("/{}".format(expected_token))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("location", resp.headers)
        self.assertEqual(resp.headers["location"], url)

    def test_invalid_url(self):
        url = "qwerty"
        resp = self.app.post("/shortenURL", json={"url": url})
        self.assertEqual(resp.status_code, 400)

    def test_token_not_exists(self):
        expected_token = "5AGfz"
        resp = self.app.post("/getURL", json={"token": expected_token})
        self.assertEqual(resp.status_code, 404)
