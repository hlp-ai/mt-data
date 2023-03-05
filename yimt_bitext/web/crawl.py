"""5. Crawl multilingual entries"""
from yimt_bitext.base import BasicUrlsToCrawl, BasicUrlsCrawled, BasicCrawler, BasicPageParser, BasicSentenceSplitter
from yimt_bitext.web import URL


to_crawl_fn = "./CC-MAIN-2022-40/urls_tocrawl.txt"
to_crawl = BasicUrlsToCrawl(to_crawl_fn)
crawled = BasicUrlsCrawled()
crawler = BasicCrawler()
parser = BasicPageParser()
sentence_splitter = BasicSentenceSplitter()

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
        print(sentences)

        # crawl in-site
        u = URL(url)
        site = u.scheme + "://" + u.netloc + "/"
        outlinks = list(filter(lambda ol: ol.startswith(site), outlinks))
        for ol in outlinks:
            to_crawl.add(ol)

        crawled.add(url)

    print(len(crawled), len(to_crawl))
