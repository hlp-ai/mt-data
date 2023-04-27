"""5. Crawl multilingual entries"""
import sys

from yimt_bitext.web.base import BasicUrlsToCrawl, BasicUrlsCrawled, BasicCrawler, BasicPageParser, \
    BasicSentenceSplitter, BasicLangID, BasicSentenceRepo, SentenceRepoFile, DiskUrlsCrawled
from yimt_bitext.web.web import URL


if __name__ == "__main__":
    to_crawl_fn = sys.argv[1]  # "../CC-MAIN-2022-40/urls_tocrawl.txt"

    to_crawl = BasicUrlsToCrawl(to_crawl_fn)
    crawled = DiskUrlsCrawled()  # BasicUrlsCrawled()
    crawler = BasicCrawler()
    parser = BasicPageParser()
    sentence_splitter = BasicSentenceSplitter()
    langid = BasicLangID()
    sent_repo = SentenceRepoFile(accepted_langs=["zh", "en", "ko"])

    while True:
        url = to_crawl.next()
        if url is None:
            break
        print("Fetching", url)
        html_content = crawler.crawl(url)
        if html_content is not None:
            print("Parsing", url)
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
            print(sent_repo)

            # crawl in-site
            u = URL(url)
            site = u.scheme + "://" + u.netloc + "/"
            outlinks = list(filter(lambda ol: ol.startswith(site), outlinks))
            for ol in outlinks:
                to_crawl.add(ol)

            crawled.add(url)

        print(len(crawled), "crawled,", len(to_crawl), "to crawl.")
