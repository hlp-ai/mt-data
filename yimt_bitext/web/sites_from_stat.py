import sys

from yimt_bitext.web.base import BasicLangStat

if __name__ == "__main__":
    stat_f = sys.argv[1]
    langs = sys.argv[2].split(",")
    lang_stat = BasicLangStat(stat_f)
    out_f = "sites-" + "-".join(langs) + ".txt"

    with open(out_f, "w", encoding="utf-8") as f:
        for host in lang_stat.hosts_for_langs(langs):
            f.write(host + "\n")
