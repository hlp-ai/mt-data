"""4. Crawl multilingual domain for TEST"""
import argparse

from yimt_bitext.web.crawl import crawl_domain

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--domain_dir", default=None, help="Directory for domain")
    argparser.add_argument("--langs", required=True, help="2-letter language code list seperated with comma")
    args = argparser.parse_args()

    accepted_langs = args.langs.split(",")
    path = args.domain_dir

    crawl_domain(path, accepted_langs)
