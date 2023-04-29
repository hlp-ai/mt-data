from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

from yimt_bitext.web import url_language
from yimt_bitext.web.url_language import UrlLanguage
from yimt_bitext.web.web import URL


class UrlFilter:

    def filter(self, url):
        pass


class BasicUrlFilter(UrlFilter):
    def __init__(self, domain, langs):
        self.domain = domain
        self.langs = langs
        self._url_lang = UrlLanguage()

    def filter(self, url):
        url = url.lower()
        if url.find(self.domain) < 0:
            return False

        u = URL(url)
        path = u.path
        filtered_type = [".pdf", ".doc", ".docx", ".ppt", ".pptx",
                         "xls", ".xlsx",
                         ".zip", ".gzip", ".rar", ".tar",
                         ".jpg", ".jpeg", ".gif", "png",
                         ".bin", ".exe"]
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

    def __init__(self, ser_file="crawled.txt"):
        self._ids = set()
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
        if len(self) % 10 == 0:
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


class BasicUrlsToCrawl(UrlsToCrawl):

    def __init__(self, path):
        self._urls = []
        self._ids = set()
        self.ser_path = path
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

        if len(self) % 50 == 0:
            with open(self.ser_path, "w", encoding="utf-8") as f:
                for u in self._urls:
                    f.write(u + "\n")

    def next(self):
        if len(self._urls) == 0:
            return None

        return self._urls.pop()

    def __len__(self):
        return len(self._urls)


class Fetcher:

    def crawl(self, url):
        pass


class BasicFetcher(Fetcher):

    def __init__(self, timeout=(15, 15)):
        self._timeout = timeout

    def crawl(self, url):
        try:
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)'}
            r = requests.get(url, headers=header, timeout=self._timeout)

            if r.status_code == 200:
                r.encoding = r.apparent_encoding
                return r.text
            else:
                return None
        except Exception as e:
            print("Exception for {}: {}".format(url, e))
            return None


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
    crawler = BasicFetcher()
    pageparser = BasicPageParser()

    url1 = "http://www.hust.edu.cn"
    r = crawler.crawl(url1)
    print(r)

    if r:
        txt, outlinks = pageparser.parse(r, url1)
        print(txt)
        print(outlinks)

    r = crawler.crawl("http://www.google.com")
    print(r)
