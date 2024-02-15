""""2. Calculate statistics on languages of text from metadata file"""
import argparse
import glob
import os
import shutil

from yimt_bitext.web.cc import update_k2dict
from yimt_bitext.web.lang_stat import BasicLangStat


def stat_from_meta_by_host(meta_file):
    """For multilingual site"""
    host2lang2len = {}

    report_interval = 10000
    total = 0

    with open(meta_file, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            url, host, domain, lang, content_len = parts
            content_len = int(content_len)

            update_k2dict(host2lang2len, host, lang, content_len)

            total += 1
            if total % report_interval == 0:
                print(" ", total, "urls processed")
        print(" ", total, "urls processed")

    return host2lang2len


def stat_from_metadata(meta_dir):
    processed_meta_dir = os.path.join(meta_dir, "processed_meta")
    if not os.path.exists(processed_meta_dir):
        os.mkdir(processed_meta_dir)

    lang_stat = BasicLangStat(os.path.join(meta_dir, "domain2host2lang2len.json"))
    print("# of domains before:", lang_stat.size())

    meta_files = glob.glob(os.path.join(meta_dir, "*.meta"))
    if len(meta_files) == 0:
        print("No meta file to process.")

    total = len(meta_files)
    done = 0
    for f in meta_files:
        print("Stating from metadata file {}: {}/{}".format(f, done, total))
        host2lang2len_local = stat_from_meta_by_host(f)
        for host, lang2len in host2lang2len_local.items():
            lang_stat.update(host, lang2len)

        shutil.move(f, processed_meta_dir)

        print("# of domains after:", lang_stat.size())

        done += 1

    lang_stat.save()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--meta_dir", required=True, help="Directory of metadata file")
    args = argparser.parse_args()

    meta_dir = args.meta_dir
    if not os.path.exists(meta_dir):
        print("{} not exist.".format(meta_dir))
    else:
        stat_from_metadata(meta_dir)
