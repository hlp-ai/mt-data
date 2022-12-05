"""1. Count the total lengths of text with different languages for hosts from WET file of CommonCrawl"""
import argparse
import json
import os

from yimt_bitext.cc import count_lang

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--wet_path", type=str, required=True, help="WET file")
    argparser.add_argument("--stat_path", type=str, default="./stat_host.json", help="stat file")
    args = argparser.parse_args()

    wet_path = args.wet_path
    stat_path = args.stat_path

    host2lang2len = {}

    if os.path.exists(stat_path):
        with open(stat_path, encoding="utf-8") as f:
            print("Loading stat file for updating...")
            host2lang2len = json.load(f)

    print("# hosts: ", len(host2lang2len))

    new_hosts = count_lang(wet_path, host2lang2len)

    print("# new hosts: ", new_hosts)
    print("# hosts: ", len(host2lang2len))
    print("Writing stat file...")
    with open(stat_path, "w", encoding="utf-8") as stream:
        json.dump(host2lang2len, stream)

