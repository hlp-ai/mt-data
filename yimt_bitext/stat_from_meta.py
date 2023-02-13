""""2. Calculate statistics from metadata file"""
import argparse
import glob
import json
import os

from yimt_bitext.cc import stat_from_meta, merge_k2dict, merge_k2set

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--meta_dir", required=True, help="Directory of metadata file")
    args = argparser.parse_args()

    meta_files = glob.glob(os.path.join(args.meta_dir, "*.meta"))

    domain2hosts = {}
    domain2lang2len = {}

    stat_host_fn = os.path.join(args.meta_dir, "domain2hosts.json")
    stat_domain_fn = os.path.join(args.meta_dir, "domain2lang2len.json")

    update = False
    if update:
        print("Loading existing stat for updating...")
        with open(stat_host_fn, encoding="utf-8") as stream:
            domain2hosts = json.load(stream)

        with open(stat_domain_fn, encoding="utf-8") as stream:
            domain2lang2len = json.load(stream)

    for f in meta_files:
        print("Stating from metadata file ", f)
        domain2hosts_local, domain2lang2len_local = stat_from_meta(f)

        print("  # of domains found: ", len(domain2lang2len_local))

        domain2hosts = merge_k2set(domain2hosts, domain2hosts_local)
        domain2lang2len = merge_k2dict(domain2lang2len, domain2lang2len_local)

        print("  # of domains after merging: ", len(domain2lang2len))

    with open(stat_host_fn, "w", encoding="utf-8") as stream:
        json.dump(domain2hosts, stream)

    with open(stat_domain_fn, "w", encoding="utf-8") as stream:
        json.dump(domain2lang2len, stream)
