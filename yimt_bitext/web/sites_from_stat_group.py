import argparse
import json
import os
from collections import defaultdict

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
    domain2hosts_langs_total = defaultdict(list)

    for d in dirs:
        meta_dir = os.path.join(group_meta_dir, d)
        print("Sites_from_stat", meta_dir)

        stat_f = os.path.join(meta_dir, "domain2host2lang2len.json")
        domain2hosts_langs = sites_from_stat(stat_f, langs)

        d = os.path.dirname(stat_f)
        out_f = os.path.join(d, "sites-" + "-".join(langs) + ".json")
        with open(out_f, "w", encoding="utf-8") as f:
            json.dump(domain2hosts_langs, f, indent=2)

        print("发现符合条件的多语域名数: {}".format(len(domain2hosts_langs)))

        for domain, hosts in domain2hosts_langs.items():
            if domain not in domain2hosts_langs_total:
                domain2hosts_langs_total[domain] = hosts
            else:
                for host in hosts:
                    if host not in domain2hosts_langs_total[domain]:
                        domain2hosts_langs_total[domain].append(host)

        total_domains_found += len(domain2hosts_langs)

    print("总共发现符合条件的多语域名数: {}".format(total_domains_found))
    out_f = os.path.join(os.path.dirname(group_meta_dir), "sites-" + "-".join(langs) + ".json")
    with open(out_f, "w", encoding="utf-8") as f:
        json.dump(domain2hosts_langs_total, f, indent=2)
