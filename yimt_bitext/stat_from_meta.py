import argparse
import glob
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
        merge_k2dict(stat_by_host, s_by_host)
        merge_k2dict(stat_by_domain, s_by_domain)

        print(len(stat_by_host), len(stat_by_domain))
