"""Get entries to crawl from dumped metadata files"""
import argparse
import json


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--candidate", type=str, default="./multidomain2langs.json", help="Candidate file path")
    argparser.add_argument("--out_path", type=str, default="./urls_tocrawl.txt", help="Urls output path")
    argparser.add_argument("--langs", type=str, nargs=2, help="three-letter language codes")
    args = argparser.parse_args()

    with open(args.candidate, encoding="utf-8") as stream:
        multidomain2langs = json.load(stream)

    with open("./CC-MAIN-2022-40/domain2hosts.json", encoding="utf-8") as stream:
        domain2hosts = json.load(stream)

    entries = set()
    lang1, lang2 = args.langs

    entries_found = 0
    report_interval = 2000
    total = 0

    for domain, langs in multidomain2langs.items():
        if lang1 in langs and lang2 in langs:
            hosts = domain2hosts[domain]
            for e in hosts:
                entries.add(e)
                entries_found += 1

        total += 1
        if total % report_interval == 0:
            print(total, entries_found)
    print(total, entries_found)

    with open(args.out_path, "w", encoding="utf-8") as stream:
        for url in entries:
            stream.write(url + "\n")
