import argparse
import json
import os

from yimt_bitext.web.sites_from_stat import sites_from_stat

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--group_meta_dir", required=True, help="Directory of group metadata file")
    argparser.add_argument("--langs", required=True, help="3-letter Language code list separated with comma")
    args = argparser.parse_args()

    group_meta_dir = args.group_meta_dir
    dirs = os.listdir(group_meta_dir)

    langs = args.langs.split(",")

    total_domains_found = 0

    for d in dirs:
        meta_dir = os.path.join(group_meta_dir, d)
        print("Sites_from_stat", meta_dir)

        stat_f = os.path.join(meta_dir, "domain2host2lang2len.json")
        domain2hosts_langs = sites_from_stat(stat_f, langs)

        d = os.path.dirname(stat_f)
        out_f = os.path.join(d, "sites-" + "-".join(langs) + ".json")

        with open(out_f, "w", encoding="utf-8") as f:
            json.dump(domain2hosts_langs, f)

        print("# of domains found: {}".format(len(domain2hosts_langs)))

        total_domains_found += len(domain2hosts_langs)

    print("总共发现符合条件的多语域名数: {}".format(total_domains_found))
