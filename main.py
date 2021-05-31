import asyncio
import re
import time
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://cfp.2021.djangocon.eu"
SPEAKER_PATH = "/2021/speaker/"


async def grab_twitter(url):
    twit_links = []
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}{url}")
    text = r.text
    soup = BeautifulSoup(text, features="html.parser")
    for link in soup("a", href=re.compile("twitter.com")):
        twit_links.append(urlparse(link["href"]).path[1:])
    return twit_links


async def grab_speakers(url):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
    text = r.text
    soup = BeautifulSoup(text, features="html.parser")
    speakers = soup.select("h3.talk-title a")
    twit_links = await asyncio.gather(
        *[grab_twitter(speaker.attrs["href"]) for speaker in speakers]
    )
    # flatten and de-dup
    handles = {item for elem in twit_links for item in elem if item}
    print(",".join(handles))


if __name__ == "__main__":
    tic = time.perf_counter()
    asyncio.run(grab_speakers(f"{BASE_URL}{SPEAKER_PATH}"))
    toc = time.perf_counter()
    print(f"Downloaded speakers in {toc - tic:0.4f} seconds")
