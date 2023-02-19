import requests
from bs4 import BeautifulSoup


def fetch(u):
    r = requests.get(u)
    return r


def parse(h):
    d = BeautifulSoup(h, "lxml")
    txt = d.get_text()
    aa = d.find_all("a")
    urls = []
    for a in aa:
        if a.has_attr("href"):
            urls.append(a["href"])

    return txt, urls


to_crawl_fn = "./CC-MAIN-2022-40/urls_tocrawl.txt"
with open(to_crawl_fn, encoding="utf-8") as f:
    for url in f:
        url = url.strip()
        print("Fetching", url)
        r = fetch(url)
        if r.status_code == 200:
            print("Parsing", url)
            t, u = parse(r.text)
            print(u)
