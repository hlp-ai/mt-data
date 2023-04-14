"""Interface for core concepts"""
import json
import os
from urllib.parse import urljoin

import langid
import requests
from bs4 import BeautifulSoup

from yimt_bitext.web.web import URL


class WetParser:

    def __init__(self, wet_file):
        self.wet_file = wet_file

    def parse(self):
        """Generator of parsed result

        :return: dict of parsed result
        """
        pass


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

    def __init__(self, timeout=20):
        self._timeout = timeout

    def crawl(self, url):
        try:
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)'}
            r = requests.get(url, headers=header, timeout=self._timeout)
        except Exception as e:
            print("Exception for {}: {}".format(url, e))
            return None

        if r.status_code == 200:
            r.encoding = "utf-8"  # TODO: How to parse text correctly?
            return r.text
        else:
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


def get_domain(host):
    u = URL(host)
    domain = u.fld
    return domain


class LangStat:

    def update(self, host, lang2len):
        pass

    def stat_by_domain(self, domain):
        pass

    def stat_by_host(self, host):
        pass

    def lang2len_by_domain(self, domain):
        pass

    def lang2len_by_host(self, host):
        return self.stat_by_host(host)

    def domains(self):
        pass

    def hosts(self, domain):
        pass

    def size(self):
        pass

    def save(self):
        pass


def merge_lang2len(old_lang2len, new_lang2len):
    for lang, length in new_lang2len.items():
        if lang not in old_lang2len:
            old_lang2len[lang] = length
        else:
            old_lang2len[lang] += length

    return old_lang2len


class BasicLangStat(LangStat):

    def __init__(self, stat_file):
        self.stat_file = stat_file
        if os.path.exists(self.stat_file):
            with open(stat_file, encoding="utf-8") as stream:
                self.stat = json.load(stream)
        else:
            self.stat = {}

    def update(self, host, lang2len):
        domain = get_domain(host)
        if domain not in self.stat:
            self.stat[domain] = {host: lang2len}
        else:
            host2lang2len = self.stat[domain]
            if host not in host2lang2len:
                host2lang2len[host] = lang2len
            else:
                old_lang2len = host2lang2len[host]
                merge_lang2len(old_lang2len, lang2len)

    def stat_by_domain(self, domain):
        if domain not in self.stat:
            return None
        else:
            return self.stat[domain]

    def stat_by_host(self, host):
        domain = get_domain(host)
        if domain not in self.stat:
            return None
        else:
            host2lang2len = self.stat[domain]
            if host not in host2lang2len:
                return None
            else:
                return host2lang2len[host]

    def lang2len_by_domain(self, domain):
        host2lang2len = self.stat_by_domain(domain)
        if host2lang2len is None:
            return None

        lang2len_ret = {}
        for host, lang2len in host2lang2len.items():
            lang2len_ret = merge_lang2len(lang2len_ret, lang2len)

        return lang2len_ret

    def domains(self):
        return self.stat.keys()

    def hosts(self, domain):
        if domain not in self.stat:
            return None

        return self.stat[domain].keys()

    def size(self):
        return len(self.stat)

    def save(self):
        with open(self.stat_file, "w", encoding="utf-8") as stream:
            json.dump(self.stat, stream)


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


if __name__ == "__main__":
    crawler = BasicCrawler()
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