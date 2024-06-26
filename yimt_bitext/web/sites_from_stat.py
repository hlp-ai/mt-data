"""3. 获得包含给定语言列表的多语域名及其站点"""
import argparse
import json
import os
from collections import defaultdict

from yimt_bitext.web.lang_stat import BasicLangStat
from yimt_bitext.web.url_language import UrlLanguage


def sites_from_stat(stat_f, langs):
    lang_stat = BasicLangStat(stat_f)

    url_language = UrlLanguage()
    normalized_langs = [url_language.normalize_lang_code(lang) for lang in langs]

    domain2hosts_langs = defaultdict(list)
    for domain, hosts in lang_stat.hosts_for_langs(langs):
        for host in hosts:
            lang = url_language.find_language(host)
            if lang and lang not in normalized_langs:  # 能通过URL启发式语言过滤
                print(host, "filtered")
                continue
            domain2hosts_langs[domain].append(host)

    return domain2hosts_langs


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--stat_file", required=True, help="Stat file")
    argparser.add_argument("--langs", required=True, help="3-letter Language code list separated with comma")
    argparser.add_argument("--out", default=None, help="output file")
    args = argparser.parse_args()

    stat_f = args.stat_file
    langs = args.langs.split(",")
    domain2hosts_langs = sites_from_stat(stat_f, langs)

    if args.out is None:
        d = os.path.dirname(stat_f)
        out_f = os.path.join(d, "sites-" + "-".join(langs) + ".json")
    else:
        out_f = args.out

    with open(out_f, "w", encoding="utf-8") as f:
        json.dump(domain2hosts_langs, f)

    print("# of domains found: {}".format(len(domain2hosts_langs)))
