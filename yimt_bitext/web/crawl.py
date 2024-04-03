"""4. Crawl multilingual domain"""
import argparse
import json
import os
from concurrent.futures._base import ALL_COMPLETED, wait
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

from yimt_bitext.utils.log import get_logger
from yimt_bitext.web.base import BasicSentenceSplitter, BasicLangID, SentenceRepoFile, BasicSentenceRepo
from yimt_bitext.web.crawl_base import BasicUrlsToCrawl, DiskUrlsCrawled, BasicFetcher, BasicPageParser, BasicUrlFilter


crawl_conf_fn = "./crawl.json"
with open(crawl_conf_fn, encoding="utf-8") as f:
    crawl_conf = json.load(f)

LANG_BALANCE_RATIO = crawl_conf["lang_balance_ratio"]  # 语言文本最大相差倍数
CHECK_BALANCE_AFTER = crawl_conf["check_balance_after"]  # 抓取多少个链接后检查语言不平衡
MAX_SINGLE_COUNT = crawl_conf["max_single_count"]  # 域名只有单个语言文本时，单个文本允许的上限
STOP_WHEN_IMBALANCE = crawl_conf["stop_when_imbalance"]  # 语言分布失衡时是否终止抓取
SENT_REPO_FLUSH_INTERVAL = crawl_conf["sent_repo_flush_interval"]  # 每抓取多少个链接保存一次句子

MAX_URL_LENGTH = 512
MAX_PAGE_LENGTH = 1024 * 1024 * 16

MAX_URLS_PER_DOMAIN = crawl_conf["max_urls_per_domain"]  # 每个域名最大抓取链接数


def is_imbalanced(counts, crawled):
    if len(counts) > 1:
        min_count = counts[0][0]
        max_count = counts[-1][0]
        if crawled > CHECK_BALANCE_AFTER and max_count > LANG_BALANCE_RATIO * min_count:  # 最少和最多语言文本数量相差过大
            return True
        else:
            return False
    else:
        count = counts[0][0]
        if crawled > CHECK_BALANCE_AFTER and count > MAX_SINGLE_COUNT:
            return True
        else:
            return False


def crawl_domain(domain_path, lang_list):
    """抓取给定域名中接受语言的链接"""
    domain = os.path.basename(domain_path)
    logger = get_logger(os.path.join(domain_path, "logs.txt"), domain)
    logger.info(f"开始抓取域名: {domain}")

    to_crawl_fn = os.path.join(domain_path, "urls_tocrawl.txt")
    crawled_fn = os.path.join(domain_path, "crawled.txt")
    sent_dir = os.path.join(domain_path, "lang2sents")

    to_crawl = BasicUrlsToCrawl(to_crawl_fn)
    crawled = DiskUrlsCrawled(crawled_fn)
    fetcher = BasicFetcher()
    parser = BasicPageParser()
    sentence_splitter = BasicSentenceSplitter()
    langid = BasicLangID()
    sent_repo = BasicSentenceRepo(sent_dir)
    url_filter = BasicUrlFilter(domain, lang_list)

    imbalanced = False

    while True:
        if STOP_WHEN_IMBALANCE and imbalanced:
            logger.info(f"由于语言分布极度失衡，停止抓取: {domain}")
            break

        url = to_crawl.next()  # 下一个待抓取链接
        if url is None:
            break

        if crawled.exists(url):  # 已经抓取过
            continue

        try:
            logger.info(f"抓取: {url}")

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
                if len(html_content)<MAX_PAGE_LENGTH:
                    # print("Parsing", url)
                    logger.debug(f"解析网页: {url}")
                    txt, outlinks = parser.parse(html_content, url)  # 提取文本和出链

                    sentences = sentence_splitter.split(txt)  # 获取非空文本段落列表
                    lang2sentences = {}
                    for s in sentences:
                        lang = langid.detect(s)  # 检测段落语言
                        if lang_list is not None and lang not in lang_list:  # 非期望语言文本
                            continue

                        if lang in lang2sentences:
                            lang2sentences[lang].append(s)
                        else:
                            lang2sentences[lang] = [s]

                    if len(lang2sentences) > 0:
                        sent_repo.store(lang2sentences)  # 保存各语言文本
                        logger.info(domain + ": " + str(sent_repo))

                        # 检测当前各语言文本数量分布
                        counts = sent_repo.sizes()

                        imbalanced = is_imbalanced(counts, len(crawled))
                        if imbalanced:
                            logger.warning("{}: 多语域名下语言分布相差过大！".format(domain))
                    else:
                        logger.debug("网页没有抽取到句子: {}".format(url))

                    # 将出链添加到待抓取列表
                    for ol in outlinks:
                        if len(ol) > MAX_URL_LENGTH:
                            logger.warning(f"太长URL过滤: {ol}")
                            continue

                        if url_filter.accept(ol):  # 过滤出链
                            to_crawl.add(ol)
                        else:
                            logger.debug(f"过滤: {ol}")
                else:
                    logger.warning(f"太长内容: {url}")

            n_tocrawl = len(to_crawl)
            n_crawled = len(crawled)
            logger.info(f"{domain}: {n_crawled} crawled, {n_tocrawl} to crawl")

            if n_crawled % SENT_REPO_FLUSH_INTERVAL == 0:
                sent_repo.flush()

            if n_crawled > MAX_URLS_PER_DOMAIN:
                imbalanced = True
                logger.warning(f"{domain}: 达到最大抓取链接数")
        except Exception as e:
            logger.warning(url + ": " + str(e))
            crawled.add(url)

    crawled.close()
    sent_repo.close()

    logger.info(f"抓取结束: {domain}")


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
                self.logger.info("发现新域名: {}".format(domain))
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
                            self.logger.info("发现新主机: {}".format(s))
                            f.write(s + "\n")

    def start_crawl(self, accepted_langs, max_workers=6):
        pool = ThreadPoolExecutor(max_workers=max_workers)
        domain_paths = []
        for domain in os.listdir(self.crawl_dir):
            domain_path = os.path.join(self.crawl_dir, domain)
            domain_paths.append(domain_path)
        self.logger.info("抓取域名数: {}".format(len(domain_paths)))

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
