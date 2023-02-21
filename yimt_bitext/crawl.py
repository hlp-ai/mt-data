from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def fetch(u):
    try:
        r = requests.get(u)
    except Exception:
        print("Exception")
        return None
    return r


def parse(base, h):
    d = BeautifulSoup(h, "lxml")
    txt = d.get_text()
    aa = d.find_all("a")
    urls = []
    for a in aa:
        if a.has_attr("href"):
            au = urljoin(base, a["href"])
            urls.append(au)

    urls = list(filter(lambda u: u.startswith(base), urls))

    return txt, urls


to_crawl_fn = "./CC-MAIN-2022-40/urls_tocrawl.txt"
with open(to_crawl_fn, encoding="utf-8") as f:
    for url in f:
        url = url.strip()
        print("Fetching", url)
        r = fetch(url)
        if r is not None and r.status_code == 200:
            print("Parsing", url)
            t, u = parse(url, r.text)
            print(u)

