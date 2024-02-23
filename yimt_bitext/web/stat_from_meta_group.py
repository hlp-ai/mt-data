import argparse
import os

from yimt_bitext.web.stat_from_meta import stat_from_metadata

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--group_meta_dir", required=True, help="Directory of group metadata file")
    argparser.add_argument("--remove", action="store_true", help="Delete meta file or not")
    args = argparser.parse_args()

    group_meta_dir = args.group_meta_dir
    dirs = os.listdir(group_meta_dir)
    total_domains = 0
    for d in dirs:
        meta_dir = os.path.join(group_meta_dir, d)
        print("Stat_from_medata", meta_dir)
        n = stat_from_metadata(meta_dir, args.remove)
        total_domains += n

    print("总共发现域名数:", total_domains)