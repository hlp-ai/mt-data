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
            r.encoding = r.apparent_encoding
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
        """host2lang2len for the given domain"""
        pass

    def stat_by_host(self, host):
        """lang2len for the given host"""
        pass

    def lang2len_by_domain(self, domain):
        """lang2len for the given domain"""
        pass

    def lang2len_by_host(self, host):
        return self.stat_by_host(host)

    def domains(self):
        """domain list"""
        pass

    def hosts(self, domain):
        """the host list in the domain"""
        pass

    def size(self):
        """number of domains"""
        pass

    def save(self):
        pass

    def domains_for_langs(self, langs):
        pass

    def hosts_for_langs(self, langs):
        pass

    @classmethod
    def languages(cls, lang2len):
        total_langs = len(lang2len.keys())
        total_lens = sum(lang2len.values())
        avg_len = total_lens / total_langs
        ret = []
        for lang in lang2len.keys():
            if lang2len[lang] > avg_len/5:
                ret.append(lang)

        return ret


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
            print("Loading stat from", self.stat_file)
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

    def domains_for_langs(self, langs):
        for domain in self.domains():
            lang2len = self.lang2len_by_domain(domain)
            found = True
            for lang in langs:
                if lang not in lang2len.keys():
                    found = False
                    break
            if found:
                yield domain

    def hosts_for_langs(self, langs):
        for domain in self.domains_for_langs(langs):
            hosts = []
            host2lang2len = self.stat_by_domain(domain)
            for host, lang2len in host2lang2len.items():
                for lang in langs:
                    if lang in lang2len.keys():
                        hosts.append(host)
                        break
            yield domain, hosts


class SentenceRepo:

    def store(self, sentences):
        pass


class BasicSentenceRepo(SentenceRepo):

    def __init__(self, path="./"):
        self.path = path
        self.repo = {}

    def store(self, lang2sentences):
        for lang, sents in lang2sentences.items():
            if lang not in self.repo:
                self.repo[lang] = []
            self.repo[lang] += sents

    def __str__(self):
        description= ""
        for lang, sents in self.repo.items():
            description += lang + ": " + str(len(sents)) + "; "
        return description


class SentenceRepoFile(SentenceRepo):

    def __init__(self, path="./lang2sents", accepted_langs=None):
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        self.path = path
        self.lang2f = {}
        self.lang2len = {}
        self.accepted_langs = accepted_langs

    def store(self, lang2sentences):
        for lang, sents in lang2sentences.items():
            if self.accepted_langs is not None and lang not in self.accepted_langs:
                continue
            if lang not in self.lang2f:
                self.lang2f[lang] = open(os.path.join(self.path, lang + ".txt"), "a", encoding="utf-8")
                self.lang2len[lang] = 0
            for s in sents:
                self.lang2f[lang].write(s + "\n")
            self.lang2len[lang] += len(sents)

    def __str__(self):
        description= ""
        for lang, count in self.lang2len.items():
            description += lang + ": " + str(count) + "; "
        return description


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
