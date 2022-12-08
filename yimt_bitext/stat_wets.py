"""1. Count the total lengths of text with different languages for hosts from WET file of CommonCrawl"""
import argparse
import json
import os

from yimt_bitext.cc import count_lang, get_wet_name, download_progress, ungzip, cc_base_url

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--wet_paths", default="./wet.paths", help="WET list file")
    argparser.add_argument("--stat_path", default="./stat_host.json", help="stat file")
    args = argparser.parse_args()

    wet_paths = args.wet_paths
    stat_path = args.stat_path

    host2lang2len = {}

    if os.path.exists(stat_path):
        with open(stat_path, encoding="utf-8") as f:
            print("Loading stat file for updating...")
            host2lang2len = json.load(f)

    print("# hosts: ", len(host2lang2len))

    with open(wet_paths, encoding="utf-8") as f:
        for wet_url in f:  # for each wet file in cc archive
            wet_url = cc_base_url + wet_url.strip()
            print("Counting from ", wet_url)
            wet_gz_path, wet_path = get_wet_name(wet_url)
            # download WET file
            download_progress(wet_url, wet_gz_path)
            ungzip(wet_gz_path, wet_path)

            new_hosts = count_lang(wet_path, host2lang2len)

            print("# new hosts: ", new_hosts)
            print("# hosts: ", len(host2lang2len))

    print("Writing stat file...")
    with open(stat_path, "w", encoding="utf-8") as stream:
        json.dump(host2lang2len, stream)

