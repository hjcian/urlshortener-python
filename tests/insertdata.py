import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import requests


def shortenURL(url):
    server = "http://localhost:12345/shortenURL"
    data = {
       "url": url
    }
    resp = requests.post(server, json=data)
    print(url, resp)


if __name__ == "__main__":
    current = Path(__file__).resolve()
    datapath = current.parent.joinpath("data.json")
    data = json.load(datapath.open("r"))
    urls = data["urls"]

    with ThreadPoolExecutor(max_workers=1000) as Executor:
        futures = [
            Executor.submit(shortenURL, url) for url in urls[34000:40000]
            ]
        results = [future.result() for future in futures]
