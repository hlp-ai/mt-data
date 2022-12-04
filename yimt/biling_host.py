"""2. Output the hosts with bilingual text"""
import argparse
import json
import os

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--out_path", type=str, default="./biling_hosts.txt", help="output file path")
    argparser.add_argument("--stat_path", type=str, default="./stat_host.json", help="stat file")
    args = argparser.parse_args()

    stat_path = args.stat_path
    biling_hosts_path = args.out_path

    with open(stat_path, encoding="utf-8") as f:
        print("Loading stat file...")
        host2lang2len = json.load(f)

    if os.path.exists(biling_hosts_path):
        with open(biling_hosts_path, encoding="utf-8") as f:
            biling_hosts = set([line.strip() for line in f])
    else:
        biling_hosts = set()

    print("# of candidate bilingual hosts: ", len(biling_hosts))
    print("# hosts for analysis: ", len(host2lang2len))

    lang1 = "zho"
    lang2 = "kor"

    new_biling_hosts = 0

    with open(biling_hosts_path, "a", encoding="utf-8") as f:
        for host, lang2len in host2lang2len.items():
            if host in biling_hosts:
                continue
            if lang1 in lang2len and lang2 in lang2len:
                f.write(host + "\n")
                new_biling_hosts += 1

    print("# of new candidate bilingual hosts found: ", new_biling_hosts)
