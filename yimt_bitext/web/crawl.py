"""5. Crawl multilingual entries"""
import os
import sys

from yimt_bitext.web.base import  BasicSentenceSplitter, BasicLangID, SentenceRepoFile
from yimt_bitext.web.crawl_base import BasicUrlsToCrawl, DiskUrlsCrawled, BasicFetcher, BasicPageParser
from yimt_bitext.web.web import URL


class DomainCrawler:

    def __init__(self, path, accepted_langs, domain=None):
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

    def crawl(self):
        while True:
            url = self.to_crawl.next()
            if url is None:
                break
            print("Fetching", url)
            html_content = self.fetcher.crawl(url)
            if html_content is not None:
                print("Parsing", url)
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
                print(self.sent_repo)

                # crawl in-site
                u = URL(url)
                site = u.scheme + "://" + u.netloc + "/"
                outlinks = list(filter(lambda ol: ol.startswith(site), outlinks))
                for ol in outlinks:
                    self.to_crawl.add(ol)

                self.crawled.add(url)

            print(len(self.crawled), "crawled,", len(self.to_crawl), "to crawl.")


if __name__ == "__main__":
    path = sys.argv[1]

    accepted_langs = ["zh", "en", "ko"]

    crawler = DomainCrawler(path, accepted_langs=accepted_langs)
    crawler.crawl()
