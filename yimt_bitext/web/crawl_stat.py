import argparse
import os
import sys
from collections import Counter


def count_lines(fn):
    if not os.path.exists(fn):
        return None

    with open(fn, encoding="utf-8") as f:
        return len(f.readlines())


def done(log_fn):
    if not os.path.exists(log_fn):
        return None

    with open(log_fn, encoding="utf-8") as f:
        for line in f:
            if line.find("抓取结束:") > 0:
                return True

    return False


def stat(domain_dir):
    crawled_fn = os.path.join(domain_dir, "crawled.txt")
    to_crawl_fn = os.path.join(domain_dir, "urls_tocrawl.txt")
    log_fn = os.path.join(domain_dir, "logs.txt")
    sents_dir = os.path.join(domain_dir, "lang2sents")

    n_crawled = count_lines(crawled_fn)
    n_tocrawl = count_lines(to_crawl_fn)

    lang_d = {}
    if os.path.exists(sents_dir):
        langs_fn = os.listdir(sents_dir)
        for fn in langs_fn:
            lang_d[fn] = count_lines(os.path.join(sents_dir, fn))

    finished = done(log_fn)

    print("Done:", finished, "# of crawled:", n_crawled, "# of tocrawl:", n_tocrawl, lang_d)

    return lang_d


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--dir", required=True, help="crawl dir")
    argparser.add_argument("--root", action="store_true", help="cout subdirectory or not")
    args = argparser.parse_args()


    lang_stat = Counter()

    if not args.root:
        lang_stat = stat(args.dir)
    else:
        dirs = os.listdir(args.dir)
        for d in dirs:
            print(d)
            s = stat(os.path.join(args.dir, d))
            lang_stat.update(s)
            print()

    print(lang_stat)
