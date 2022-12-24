""""2. Calculate statistics from metadata file"""
import argparse
import glob
import json
import os

from yimt_bitext.cc import stat_from_meta, merge_k2dict

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--meta_dir", required=True, help="Directory of metadata file")
    args = argparser.parse_args()

    meta_files = glob.glob(os.path.join(args.meta_dir, "*.meta"))

    stat_by_host = {}
    stat_by_domain = {}

    for f in meta_files:
        print("Stating from metadata file ", f)
        s_by_host, s_by_domain = stat_from_meta(f)

        print("# of hosts: ", len(s_by_host), " # of domains: ", len(s_by_domain))

        stat_by_host = merge_k2dict(stat_by_host, s_by_host)
        stat_by_domain = merge_k2dict(stat_by_domain, s_by_domain)

        print("# of hosts: ", len(stat_by_host), " # of domains: ", len(stat_by_domain))

    print("# of hosts: ", len(stat_by_host), " # of domains: ", len(stat_by_domain))

    stat_host_fn = os.path.join(args.meta_dir, "stat_by_host.json")
    stat_domain_fn = os.path.join(args.meta_dir, "stat_by_domain.json")

    with open(stat_host_fn, "w", encoding="utf-8") as stream:
        json.dump(stat_by_host, stream)

    with open(stat_domain_fn, "w", encoding="utf-8") as stream:
        json.dump(stat_by_domain, stream)
