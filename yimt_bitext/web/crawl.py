"""4. Crawl multilingual domain"""
import json
import os
import sys

from yimt_bitext.utils.log import get_logger
from yimt_bitext.web.base import  BasicSentenceSplitter, BasicLangID, SentenceRepoFile
from yimt_bitext.web.crawl_base import BasicUrlsToCrawl, DiskUrlsCrawled, BasicFetcher, BasicPageParser, BasicUrlFilter


class DomainCrawler:

    def __init__(self, path, accepted_langs, domain):
        self.domain = domain
        to_crawl_fn = os.path.join(path, "urls_tocrawl.txt")
        crawled_fn = os.path.join(path, "crawled.txt")
        sent_dir = os.path.join(path, "lang2sents")

        self.to_crawl = BasicUrlsToCrawl(to_crawl_fn)
        self.crawled = DiskUrlsCrawled(crawled_fn)
        self.fetcher = BasicFetcher()
        self.parser = BasicPageParser()
        self.sentence_splitter = BasicSentenceSplitter()
        self.langid = BasicLangID()
        self.sent_repo = SentenceRepoFile(sent_dir, accepted_langs=accepted_langs)
        self.url_filter = BasicUrlFilter(domain, accepted_langs)

        self.logger = get_logger(os.path.join(path, "logs.txt"), self.domain)

    def crawl(self):
        while True:
            url = self.to_crawl.next()
            if url is None:
                break
            # print("Fetching", url)
            try:
                self.logger.info(f"Fetcing {url}")
                r = self.fetcher.fetch(url)
                if r.status_code != 200:
                    self.logger.warn(f"{url}: {r.status_code}")
                    continue
                if r.encoding is None:
                    self.logger.warn(f"{url}: NO Encoding detected, maybe non-text page.")
                    continue
                self.logger.info(f"{url}: {r.encoding}")
                html_content = r.text
                if html_content is not None:
                    # print("Parsing", url)
                    self.logger.debug(f"Parsing {url}")
                    txt, outlinks = self.parser.parse(html_content, url)

                    sentences = self.sentence_splitter.split(txt)
                    lang2sentenes = {}
                    for s in sentences:
                        lang = self.langid.detect(s)
                        if lang in lang2sentenes:
                            lang2sentenes[lang].append(s)
                        else:
                            lang2sentenes[lang] = [s]

                    self.sent_repo.store(lang2sentenes)
                    # print(self.sent_repo)
                    self.logger.info(self.sent_repo)

                    for ol in outlinks:
                        if self.url_filter.filter(ol):
                            self.to_crawl.add(ol)
                        else:
                            # print("Filtered:", ol)
                            self.logger.debug(f"Filtered: {ol}")

                    self.crawled.add(url)

                # print(len(self.crawled), "crawled,", len(self.to_crawl), "to crawl.")
                n_tocrawl = len(self.to_crawl)
                n_crawled = len(self.crawled)
                self.logger.info(f"{n_crawled} crawled, {n_tocrawl} to crawl")
            except Exception as e:
                self.logger.warn(url + ": " + str(e))
        # print("Finish crawling for", self.domain)
        self.logger.info(f"Finish crawling for {self.domain}")


class CrawlManager:

    def __init__(self, crawl_dir):
        self.crawl_dir = crawl_dir
        if not os.path.exists(self.crawl_dir):
            os.makedirs(self.crawl_dir, exist_ok=True)

    def update(self, sites_file):
        with open(sites_file, encoding="utf-8") as sites_f:
            domain2hosts_langs = json.load(sites_f)

        for domain, hosts in domain2hosts_langs.items():
            doamin_dir = os.path.join(self.crawl_dir, domain)
            if not os.path.exists(doamin_dir):
                os.makedirs(doamin_dir, exist_ok=True)
                with open(os.path.join(doamin_dir, "urls_tocrawl.txt"), "w", encoding="utf-8") as f:
                    for s in hosts:
                        f.write(s + "\n")


if __name__ == "__main__":
    path = sys.argv[1]
    domain = sys.argv[2]

    accepted_langs = ["zh", "en", "ko"]

    crawler = DomainCrawler(path, accepted_langs, domain)
    crawler.crawl()
