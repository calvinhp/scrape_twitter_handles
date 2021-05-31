import asyncio
import re
import time
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://cfp.2021.djangocon.eu"
SPEAKER_PATH = "/2021/speaker/"
USE_HTTP2 = False


async def grab_twitter(speakers):
    twit_handles = set()
    async with httpx.AsyncClient(http2=USE_HTTP2) as client:
        responses = await asyncio.gather(
            *[client.get(BASE_URL + speaker.attrs["href"]) for speaker in speakers]
        )
    for r in responses:
        text = r.text
        soup = BeautifulSoup(text, features="html.parser")
        for link in soup("a", href=re.compile("twitter.com")):
            twit_handles.add(urlparse(link["href"]).path[1:])
    return twit_handles


async def grab_speakers(url):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
    text = r.text
    soup = BeautifulSoup(text, features="html.parser")
    speakers = soup.select("h3.talk-title a")
    twit_handles = await grab_twitter(speakers)
    print(",".join(twit_handles))


if __name__ == "__main__":
    tic = time.perf_counter()
    asyncio.run(grab_speakers(f"{BASE_URL}{SPEAKER_PATH}"))
    toc = time.perf_counter()
    print(f"Downloaded speakers in {toc - tic:0.4f} seconds")
