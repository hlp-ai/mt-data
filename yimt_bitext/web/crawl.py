"""4. Crawl multilingual domain"""
import json
import os
import sys
from concurrent.futures.thread import ThreadPoolExecutor

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
                self.logger.info(f"Fetching {url}")
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


def crawl_domain(domain_path):
    domain = os.path.basename(domain_path)
    logger = get_logger(os.path.join(domain_path, "logs.txt"), domain)
    logger.info(f"***Start crawling thread for {domain}")

    to_crawl_fn = os.path.join(domain_path, "urls_tocrawl.txt")
    crawled_fn = os.path.join(domain_path, "crawled.txt")
    sent_dir = os.path.join(domain_path, "lang2sents")

    to_crawl = BasicUrlsToCrawl(to_crawl_fn)
    crawled = DiskUrlsCrawled(crawled_fn)
    fetcher = BasicFetcher()
    parser = BasicPageParser()
    sentence_splitter = BasicSentenceSplitter()
    langid = BasicLangID()
    sent_repo = SentenceRepoFile(sent_dir, accepted_langs=accepted_langs)
    url_filter = BasicUrlFilter(domain, accepted_langs)

    while True:
        url = to_crawl.next()
        if url is None:
            break
        # print("Fetching", url)
        try:
            logger.info(f"Fetching {url}")
            r = fetcher.fetch(url)
            if r.status_code != 200:
                logger.warn(f"{url}: {r.status_code}")
                continue
            if r.encoding is None:
                logger.warn(f"{url}: NO Encoding detected, maybe non-text page.")
                continue
            logger.info(f"{url}: {r.encoding}")
            html_content = r.text
            if html_content is not None:
                # print("Parsing", url)
                logger.debug(f"Parsing {url}")
                txt, outlinks = parser.parse(html_content, url)

                sentences = sentence_splitter.split(txt)
                lang2sentenes = {}
                for s in sentences:
                    lang = langid.detect(s)
                    if lang in lang2sentenes:
                        lang2sentenes[lang].append(s)
                    else:
                        lang2sentenes[lang] = [s]

                sent_repo.store(lang2sentenes)
                # print(self.sent_repo)
                logger.info(sent_repo)

                for ol in outlinks:
                    if url_filter.filter(ol):
                        to_crawl.add(ol)
                    else:
                        # print("Filtered:", ol)
                        logger.debug(f"Filtered: {ol}")

                crawled.add(url)

            # print(len(self.crawled), "crawled,", len(self.to_crawl), "to crawl.")
            n_tocrawl = len(to_crawl)
            n_crawled = len(crawled)
            logger.info(f"{n_crawled} crawled, {n_tocrawl} to crawl")
        except Exception as e:
            logger.warn(url + ": " + str(e))
    # print("Finish crawling for", self.domain)
    logger.info(f"***Finish crawling for {domain}")


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
                print("Found new domain:", domain)
                os.makedirs(doamin_dir, exist_ok=True)
                with open(os.path.join(doamin_dir, "urls_tocrawl.txt"), "w", encoding="utf-8") as f:
                    for s in hosts:
                        f.write(s + "\n")

    def start_crawl(self, max_workers=6):
        pool = ThreadPoolExecutor(max_workers=max_workers)
        domain_paths = []
        for domain in os.listdir(self.crawl_dir):
            domain_path = os.path.join(self.crawl_dir, domain)
            domain_paths.append(domain_path)
        print("# of domains:", len(domain_paths))

        pool.map(crawl_domain, domain_paths)


if __name__ == "__main__":
    # path = sys.argv[1]
    # domain = sys.argv[2]
    #
    # accepted_langs = ["zh", "en", "ko"]
    #
    # crawler = DomainCrawler(path, accepted_langs, domain)
    # crawler.crawl()

    crawl_manager = CrawlManager("./crawl-kozhen")
    accepted_langs = ["ko", "zh", "en"]
    crawl_manager.update("./sites-kor-zho.json")
    crawl_manager.start_crawl()
