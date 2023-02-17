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

    host2lang2len = {}

    host2lang2len_fn = os.path.join(args.meta_dir, "host2lang2len.json")

    update = False
    if update:
        print("Loading existing stat for updating...")
        with open(host2lang2len_fn, encoding="utf-8") as stream:
            host2lang2len = json.load(stream)

    for f in meta_files:
        print("Stating from metadata file ", f)
        host2lang2len_local = stat_from_meta(f)

        print("  # of hosts found: ", len(host2lang2len_local))

        host2lang2len = merge_k2dict(host2lang2len, host2lang2len_local)

        print("  # of hosts after merging: ", len(host2lang2len))

    with open(host2lang2len_fn, "w", encoding="utf-8") as stream:
        json.dump(host2lang2len, stream)
