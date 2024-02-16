"""4. Crawl multilingual domain"""
import argparse
import json
import os
from concurrent.futures._base import ALL_COMPLETED, wait
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
        url = to_crawl.next()  # 下一个待抓取链接
        if url is None:
            break

        if crawled.exists(url):  # 已经抓取过
            continue

        try:
            logger.info(f"Fetching {url}")

            r = fetcher.fetch(url)  # 抓取
            crawled.add(url)  # 链接添加到已抓取列表中

            if r.status_code != 200:  # 非成功抓取
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
                txt, outlinks = parser.parse(html_content, url)  # 提取文本和出链

                sentences = sentence_splitter.split(txt)  # 获取非空文本段落列表
                lang2sentenes = {}
                for s in sentences:
                    lang = langid.detect(s)  # 检测段落语言
                    if lang_list is not None and lang not in lang_list:  # 非期望语言文本
                        continue

                    if lang in lang2sentenes:
                        lang2sentenes[lang].append(s)
                    else:
                        lang2sentenes[lang] = [s]

                if len(lang2sentenes) > 0:
                    sent_repo.store(lang2sentenes)  # 保存各语言文本
                    logger.info(domain + ": " + str(sent_repo))

                    # 检测当前各语言文本数量分布
                    counts = sent_repo.sizes()
                    if len(counts) > 1:
                        min_count = counts[0][0]
                        max_count = counts[-1][0]
                        if max_count > 50 * min_count:  # 最少和最多语言文本数量相差过大，50倍
                            logger.warning("{}: 多语域名下语言分布相差过大！".format(domain))
                else:
                    logger.debug("NO sentence found for {}".format(url))

                # 将出链添加到待抓取列表
                for ol in outlinks:
                    if url_filter.accept(ol):  # 过滤出链
                        to_crawl.add(ol)
                    else:
                        logger.debug(f"Filtered: {ol}")

            n_tocrawl = len(to_crawl)
            n_crawled = len(crawled)
            logger.info(f"{domain}: {n_crawled} crawled, {n_tocrawl} to crawl")
        except Exception as e:
            logger.warning(url + ": " + str(e))
            crawled.add(url)

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
        self.logger.info("Update crawler with {}".format(sites_file))
        with open(sites_file, encoding="utf-8") as sites_f:
            domain2hosts_langs = json.load(sites_f)

        for domain, hosts in domain2hosts_langs.items():
            doamin_dir = os.path.join(self.crawl_dir, domain)
            if not os.path.exists(doamin_dir):
                self.logger.info("Found new domain: {}".format(domain))
                os.makedirs(doamin_dir, exist_ok=True)
                with open(os.path.join(doamin_dir, "urls_tocrawl.txt"), "w", encoding="utf-8") as f:
                    for s in hosts:
                        f.write(s + "\n")
            else:
                crawled_fn = os.path.join(doamin_dir, "crawled.txt")
                crawled = DiskUrlsCrawled(crawled_fn)
                with open(os.path.join(doamin_dir, "urls_tocrawl.txt"), "a", encoding="utf-8") as f:
                    for s in hosts:
                        if not crawled.exists(s):
                            self.logger.info("Found new host: {}".format(s))
                            f.write(s + "\n")

    def start_crawl(self, accepted_langs, max_workers=6):
        pool = ThreadPoolExecutor(max_workers=max_workers)
        domain_paths = []
        for domain in os.listdir(self.crawl_dir):
            domain_path = os.path.join(self.crawl_dir, domain)
            domain_paths.append(domain_path)
        self.logger.info("# of domains: {} to crawl".format(len(domain_paths)))

        tasks = pool.map(partial(crawl_domain, lang_list=accepted_langs), domain_paths)
        wait(tasks, return_when=ALL_COMPLETED)


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
