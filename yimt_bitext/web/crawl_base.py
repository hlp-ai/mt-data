import os
import random
from pprint import pprint
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

from yimt_bitext.web.url_language import UrlLanguage
from yimt_bitext.web.web import URL


class UrlFilter:

    def accept(self, url):
        pass


class BasicUrlFilter(UrlFilter):
    def __init__(self, domain, langs):
        self.domain = domain
        self.langs = langs
        self._url_lang = UrlLanguage()

    def accept(self, url):
        url = url.lower()
        if url.find(self.domain) < 0:
            return False

        if url.startswith("mailto:"):
            return False

        u = URL(url)
        path = u.path
        filtered_type = [".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
                         ".mp4", ".mp3", ".wav", ".mov", ".avi", ".rm", ".rmvb", ".mpeg",
                         ".zip", ".gzip", ".rar", ".tar", ".gz", ".7z", ".bz2", ".iso",
                         ".jpg", ".jpeg", ".gif", "png", ".bmp", ".tiff", ".webp",
                         ".bin", ".exe", ".so"]
        if len(path) > 0:
            for t in filtered_type:
                if path.endswith(t):
                    return False

        lang = self._url_lang.find_language(url)
        if len(lang) > 0 and lang not in self.langs:
            return False

        return True


class UrlsCrawled:

    def exists(self, url):
        """Is the url crawled?"""
        pass

    def add(self, url):
        """The url has been crawled"""
        pass

    def close(self):
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


class DiskUrlsCrawled(UrlsCrawled):

    def __init__(self, ser_file="crawled.txt", save_interval=10):
        self._ids = set()
        self._save_interval = save_interval
        if os.path.exists(ser_file):
            with open(ser_file, encoding="utf-8") as f:
                for u in f:
                    u = u.strip()
                    h = hash(u)
                    if h not in self._ids:
                        self._ids.add(h)

        self.ser_stream = open(ser_file, "a", encoding="utf-8")

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
        self.ser_stream.write(url + "\n")
        if len(self) %  self._save_interval == 0:
            self.ser_stream.flush()

    def __len__(self):
        return len(self._ids)

    def close(self):
        self.ser_stream.close()


class UrlsToCrawl:

    def add(self, url):
        """Add url to crawl"""
        pass

    def next(self):
        """Get url for crawling"""
        pass

    def close(self):
        pass


class BalancedUrlsToCrawl(UrlsToCrawl):

    def __init__(self, path):
        self._host2urls = []
        self._ids = set()
        self._next_host_id = 0

        with open(path, encoding="utf-8") as f:
            for url in f:
                url = url.strip()
                self.add(url)

    def add(self, url):
        """Add url to crawl"""
        h = hash(url)
        if h in self._ids:
            return
        self._ids.add(h)

        u = URL(url)
        host = u.host
        i = 0
        found = False
        while i<len(self._host2urls):
            if self._host2urls[i][0] == host:
                self._host2urls[i][1].append(url)
                found = True
                break
            else:
                i += 1

        if not found:
            self._host2urls.append((host, [url]))

    def next(self):
        """Get url for crawling"""
        if len(self._host2urls) == 0:
            return None

        if self._next_host_id >= len(self._host2urls):
            self._next_host_id -= len(self._host2urls)

        if self._next_host_id < len(self._host2urls):
            url = self._host2urls[self._next_host_id][1].pop()
            if len(self._host2urls[self._next_host_id][1]) == 0:  # 主机下没有链接了
                self._host2urls.pop(self._next_host_id)

            self._next_host_id += 1
            return url

    def close(self):
        pass


class BasicUrlsToCrawl(UrlsToCrawl):

    def __init__(self, path, save_interval=50):
        self._urls = []
        self._ids = set()
        self.ser_path = path
        self._added = 0
        self._save_interval = save_interval
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

        self._added += 1

        if self._added % self._save_interval == 0:
            with open(self.ser_path, "w", encoding="utf-8") as f:
                for u in self._urls:
                    f.write(u + "\n")

    def next(self):
        if len(self._urls) == 0:
            return None

        idx = random.randint(0, len(self._urls)-1)

        e = self._urls.pop(idx)
        return e

    def __len__(self):
        return len(self._urls)

    def close(self):
        with open(self.ser_path, "w", encoding="utf-8") as f:
            for u in self._urls:
                f.write(u + "\n")


class Fetcher:

    def crawl(self, url):
        pass


class BasicFetcher(Fetcher):

    def __init__(self, timeout=(15, 15)):
        self._timeout = timeout

    def fetch(self, url):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
        r = requests.get(url, headers=header, timeout=self._timeout)

        if r.status_code == 200:
            r.encoding = r.apparent_encoding

        return r


class PageParser:

    def parse(self, htm, url):
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


if __name__ == "__main__":
    import sys
    from yimt_bitext.web.base import BasicSentenceSplitter, BasicLangID

    fetcher = BasicFetcher()
    pageparser = BasicPageParser()
    sentence_splitter = BasicSentenceSplitter()
    langid = BasicLangID()

    url1 = sys.argv[1]

    try:
        r = fetcher.fetch(url1)
        if r.status_code == 200:
            r = r.text
            txt, outlinks = pageparser.parse(r, url1)
            print(txt)
            print(outlinks)

            sentences = sentence_splitter.split(txt)
            lang2sentenes = {}
            for s in sentences:
                lang = langid.detect(s)
                if lang in lang2sentenes:
                    lang2sentenes[lang].append(s)
                else:
                    lang2sentenes[lang] = [s]
            pprint(lang2sentenes)
        else:
            print(r.status_code)
    except Exception as e:
        print(e)

