"""4. Crawl multilingual domain"""
import sys

from yimt_bitext.web.crawl import crawl_domain

if __name__ == "__main__":
    path = sys.argv[1]

    accepted_langs = ["zh", "en", "ko"]

    crawl_domain(path, accepted_langs)
