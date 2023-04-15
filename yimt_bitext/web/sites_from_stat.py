import sys

from yimt_bitext.web.base import BasicLangStat

if __name__ == "__main__":
    stat_f = sys.argv[1]
    langs = sys.argv[2].split(",")
    lang_stat = BasicLangStat(stat_f)
    for host in lang_stat.hosts_for_langs(langs):
        print(host)
