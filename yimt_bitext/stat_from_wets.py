"""1. Count the total lengths of text with different languages for hosts from WET file of CommonCrawl"""
import argparse
import json
import os

from yimt_bitext.cc import count_lang, get_wet_name, download_progress, ungzip, cc_base_url, cc_wet_paths, \
    cc_stat_host_file, cc_wet_paths_done

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--wet_paths_dir", help="Directory of wet.paths file")
    argparser.add_argument("--dump_url", action="store_true", help="Dump urls in WET file")
    args = argparser.parse_args()

    wet_paths = os.path.join(args.wet_paths_dir, cc_wet_paths)
    stat_path = os.path.join(args.wet_paths_dir, cc_stat_host_file)
    wet_paths_done = os.path.join(args.wet_paths_dir, cc_wet_paths_done)

    wets_done = set()
    if os.path.exists(wet_paths_done):
        with open(wet_paths_done, encoding="utf-8") as f:
            for u in f:
                wets_done.add(u.strip())

    print("# of WET done: ", len(wets_done))

    host2lang2len = {}

    if os.path.exists(stat_path):  # load existing stats
        with open(stat_path, encoding="utf-8") as f:
            print("Loading stat file for updating...")
            host2lang2len = json.load(f)

    print("# hosts: ", len(host2lang2len))

    with open(wet_paths, encoding="utf-8") as f:
        for wet_url in f:  # for each wet file in cc archive
            wet_url = cc_base_url + wet_url.strip()
            if wet_url in wets_done:
                print(wet_url, " has been processed before")
                continue
            print("Counting WET file ", wet_url)
            wet_gz_name, wet_name = get_wet_name(wet_url)

            wet_gz_path = os.path.join(args.wet_paths_dir, wet_gz_name)
            wet_path = os.path.join(args.wet_paths_dir, wet_name)

            # download WET file
            download_progress(wet_url, wet_gz_path)

            # unzip WET file
            ungzip(wet_gz_path, wet_path)

            # counting
            url_file = None
            if args.dump_url:
                url_file = os.path.join(args.wet_paths_dir, wet_name + ".urls")
            new_hosts = count_lang(wet_path, host2lang2len, url_file)

            print("# new hosts: ", new_hosts)
            print("# hosts: ", len(host2lang2len))

            print("Writing stat file...")
            with open(stat_path, "w", encoding="utf-8") as stream:
                json.dump(host2lang2len, stream)

            print("Updating WET done file...")
            with open(wet_paths_done, "a", encoding="utf-8") as f:
                f.write(wet_url + "\n")
