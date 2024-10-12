import json
from urllib.parse import quote, urlparse

import requests
from bs4 import BeautifulSoup

def get_decoding_params(gn_art_id):
    response = requests.get(f"https://news.google.com/articles/{gn_art_id}")
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    div = soup.select_one("c-wiz > div")
    return {
        "signature": div.get("data-n-a-sg"),
        "timestamp": div.get("data-n-a-ts"),
        "gn_art_id": gn_art_id,
    }

def decode_urls(articles):
    articles_reqs = [
        [
            "Fbv4je",
            f'["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,null,null,0,1],"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{art["gn_art_id"]}",{art["timestamp"]},"{art["signature"]}"]',
        ]
        for art in articles
    ]
    payload = f"f.req={quote(json.dumps([articles_reqs]))}"
    headers = {"content-type": "application/x-www-form-urlencoded;charset=UTF-8"}
    response = requests.post(
        url="https://news.google.com/_/DotsSplashUi/data/batchexecute",
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    return [json.loads(res[2])[1] for res in json.loads(response.text.split("\n\n")[1])[:-2]]

def main():
    encoded_urls = [
        "https://news.google.com/read/CBMinAFBVV95cUxPQVZwY01CcTN2SXgwNXZQd0duZjE4U01wekZZSTRYZFpXT3lvamZmVjMwMzBZOW9vNEtKYlhjX3NSb0JOai1SVzZveGF2RUJiQjcxaUQxZGJ6NmhST09UdU5HUzRDSTBBblhZRnVmRXpYRXNKOWJRTXlEMFZsNGlFMGNhUGU5SGtfRDE3TUZOaHRDNGVrZHB2bndYcXA?hl=en-US&gl=US&ceid=US%3Aen"
    ]
    articles_params = [get_decoding_params(urlparse(url).path.split("/")[-1]) for url in encoded_urls]
    decoded_urls = decode_urls(articles_params)
    print(decoded_urls)

if __name__ == "__main__":
    main()
