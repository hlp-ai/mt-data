"""Interface for core concepts"""
from urllib.parse import urljoin

import langid
import requests
from bs4 import BeautifulSoup


class UrlsCrawled:

    def exists(self, url):
        """Is the url crawled?"""
        pass

    def add(self, url):
        """The url has been crawled"""
        pass


class BasicUrlsCrawled(UrlsCrawled):

    def __init__(self):
        self._ids = set()

    def exists(self, url):
        h = hash(url)
        if h in self._ids:
            return True
        else:
            return False

    def add(self, url):
        h = hash(url)
        if h in self._ids:
            return
        self._ids.add(h)

    def __len__(self):
        return len(self._ids)


class UrlsToCrawl:

    def add(self, url):
        """Add url to crawl"""
        pass

    def next(self):
        """Get url for crawling"""
        pass


class BasicUrlsToCrawl(UrlsToCrawl):

    def __init__(self, path):
        self._urls = []
        self._ids = set()
        with open(path, encoding="utf-8") as f:
            for url in f:
                url = url.strip()
                self.add(url)

    def exists(self, url):
        h = hash(url)
        if h in self._ids:
            return True
        else:
            return False

    def add(self, url):
        h = hash(url)
        if h in self._ids:
            return
        self._ids.add(h)
        self._urls.append(url)

    def next(self):
        if len(self._urls) == 0:
            return None

        return self._urls.pop()

    def __len__(self):
        return len(self._urls)


class Crawler:

    def crawl(self, url):
        pass


class BasicCrawler(Crawler):

    def __init__(self, timeout=30):
        self._timeout = timeout

    def crawl(self, url):
        try:
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)'}
            r = requests.get(url, headers=header, timeout=self._timeout)
        except Exception:
            print("Exception")
            return None

        if r.status_code == 200:
            return r.text
        else:
            return None


class PageParser:

    def parse(self, htm):
        pass


class BasicPageParser(PageParser):

    def parse(self, htm, base):
        d = BeautifulSoup(htm, "lxml")
        txt = d.get_text()
        aa = d.find_all("a")
        urls = []
        for a in aa:
            if a.has_attr("href"):
                au = urljoin(base, a["href"])
                urls.append(au)

        return txt, urls


class LangStat:

    def stat(self, text):
        pass


class LangID:

    def detect(self, text):
        pass


class BasicLangID(LangID):

    def detect(self, text):
        return langid.classify(text)[0]


class SentenceSplitter:

    def split(self, text):
        pass


class BasicSentenceSplitter(SentenceSplitter):

    def split(self, text):
        paragraphs = text.split("\n")
        paragraphs = [p.strip() for p in paragraphs]
        paragraphs = list(filter(lambda p: len(p)>0, paragraphs))

        return paragraphs


class Host2Lang2Len:

    def update(self, host, lang2len):
        """Update the language statistics of given host"""
        pass

    def get(self, host):
        """Get the language statistics of given host"""
        pass

    def next(self):
        """Iterate"""
        pass


class MultiLangHost:

    def update(self, host, lang):
        """Add lang to lang list of host"""
        pass

    def get(self, host):
        """Get the lang list of host"""
        pass

    def next(self):
        """Iterate"""
        pass


class Host2Lang2Sent:

    def update(self, host, lang, sentences):
        pass

    def get(self, host, lang):
        pass


class ProcessedWET:

    def is_processed(self, wet_url):
        pass

    def processed(self, wet_url):
        pass


class WETs:

    def add(self, cc_id):
        pass

    def next(self):
        pass