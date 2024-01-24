"""4. Crawl multilingual domain"""
import argparse
import json
import os
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

from yimt_bitext.utils.log import get_logger
from yimt_bitext.web.base import  BasicSentenceSplitter, BasicLangID, SentenceRepoFile
from yimt_bitext.web.crawl_base import BasicUrlsToCrawl, DiskUrlsCrawled, BasicFetcher, BasicPageParser, BasicUrlFilter


def crawl_domain(domain_path, lang_list):
    """抓取给定域名中接受语言的链接"""
    domain = os.path.basename(domain_path)
    logger = get_logger(os.path.join(domain_path, "logs.txt"), domain)
    logger.info(f"***START CRAWLING {domain}")

    to_crawl_fn = os.path.join(domain_path, "urls_tocrawl.txt")
    crawled_fn = os.path.join(domain_path, "crawled.txt")
    sent_dir = os.path.join(domain_path, "lang2sents")

    to_crawl = BasicUrlsToCrawl(to_crawl_fn)
    crawled = DiskUrlsCrawled(crawled_fn)
    fetcher = BasicFetcher()
    parser = BasicPageParser()
    sentence_splitter = BasicSentenceSplitter()
    langid = BasicLangID()
    sent_repo = SentenceRepoFile(sent_dir)
    url_filter = BasicUrlFilter(domain, lang_list)

    while True:
        url = to_crawl.next()
        if url is None:
            break
        # print("Fetching", url)
        try:
            logger.info(f"Fetching {url}")
            r = fetcher.fetch(url)
            if r.status_code != 200:
                logger.warning(f"{url}: {r.status_code}")
                continue
            if r.encoding is None:
                logger.warning(f"{url}: NO Encoding detected, maybe non-text page.")
                continue
            logger.debug(f"{url}: {r.encoding}")

            html_content = r.text
            if html_content is not None:
                # print("Parsing", url)
                logger.debug(f"Parsing {url}")
                txt, outlinks = parser.parse(html_content, url)

                sentences = sentence_splitter.split(txt)
                lang2sentenes = {}
                for s in sentences:
                    lang = langid.detect(s)
                    if lang_list is not None and lang not in lang_list:
                        continue
                    if lang in lang2sentenes:
                        lang2sentenes[lang].append(s)
                    else:
                        lang2sentenes[lang] = [s]

                if len(lang2sentenes) > 0:
                    sent_repo.store(lang2sentenes)
                    logger.info(sent_repo)
                else:
                    logger.debug("NO sentence found for {}".format(url))

                for ol in outlinks:
                    if url_filter.filter(ol):
                        to_crawl.add(ol)
                    else:
                        logger.debug(f"Filtered: {ol}")

                crawled.add(url)

            n_tocrawl = len(to_crawl)
            n_crawled = len(crawled)
            logger.info(f"{n_crawled} crawled, {n_tocrawl} to crawl")
        except Exception as e:
            logger.warning(url + ": " + str(e))

    crawled.close()

    logger.info(f"***FINISH CRAWLING {domain}")


class CrawlManager:

    def __init__(self, crawl_dir):
        self.crawl_dir = crawl_dir
        if not os.path.exists(self.crawl_dir):
            os.makedirs(self.crawl_dir, exist_ok=True)

        self.logger = get_logger(os.path.join(crawl_dir, "logs.txt"), "CrawlManager")

    def update(self, sites_file):
        """更新待抓取列表"""
        with open(sites_file, encoding="utf-8") as sites_f:
            domain2hosts_langs = json.load(sites_f)

        for domain, hosts in domain2hosts_langs.items():
            doamin_dir = os.path.join(self.crawl_dir, domain)
            if not os.path.exists(doamin_dir):  # TODO: 多语域名下新发现的站点的添加
                self.logger.info("Found new domain: {}".format(domain))
                os.makedirs(doamin_dir, exist_ok=True)
                with open(os.path.join(doamin_dir, "urls_tocrawl.txt"), "w", encoding="utf-8") as f:
                    for s in hosts:
                        f.write(s + "\n")

    def start_crawl(self, accepted_langs, max_workers=6):
        pool = ThreadPoolExecutor(max_workers=max_workers)
        domain_paths = []
        for domain in os.listdir(self.crawl_dir):
            domain_path = os.path.join(self.crawl_dir, domain)
            domain_paths.append(domain_path)
        self.logger.info("# of domains: {} to crawl".format(len(domain_paths)))

        pool.map(partial(crawl_domain, lang_list=accepted_langs), domain_paths)

        self.logger.info("***All CRAWL DONE.")


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--sites_file", required=True, help="sites json file")
    argparser.add_argument("--crawl_dir", default=None, help="Directory for crawling")
    argparser.add_argument("--langs", required=True, help="2-letter language code list seperated with comma")
    argparser.add_argument("--max_workers", default=8, type=int, help="Language list seperated with comma")
    args = argparser.parse_args()

    lang_list = args.langs.split(",")

    if args.crawl_dir is None:
        d = os.path.dirname(args.sites_file)
        crawl_dir = os.path.join(d, "crawl-" + "-".join(lang_list))
    else:
        crawl_dir = args.crawl_dir

    crawl_manager = CrawlManager(crawl_dir)

    crawl_manager.update(args.sites_file)
    crawl_manager.start_crawl(lang_list, args.max_workers)
