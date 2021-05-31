import re
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://cfp.2021.djangocon.eu"
SPEAKER_PATH = "/2021/speaker/"


def grab_twitter(url):
    twit_links = []
    r = requests.get(f"{BASE_URL}{url}")
    text = r.text
    soup = BeautifulSoup(text, features="html.parser")
    for link in soup("a", href=re.compile("twitter.com")):
        twit_links.append(urlparse(link["href"]).path[1:])
    return twit_links


def grab_speakers(url):
    r = requests.get(url)
    text = r.text
    soup = BeautifulSoup(text, features="html.parser")
    speakers = soup.select("h3.talk-title a")
    twit_links = []
    for speaker in speakers:
        if link := grab_twitter(speaker.attrs["href"]):
            twit_links += link
    print(",".join(twit_links))


if __name__ == "__main__":
    tic = time.perf_counter()
    grab_speakers(f"{BASE_URL}{SPEAKER_PATH}")
    toc = time.perf_counter()
    print(f"Downloaded speakers in {toc - tic:0.4f} seconds")
