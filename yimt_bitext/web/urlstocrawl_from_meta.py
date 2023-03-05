"""Get urls to crawl from dumped metadata files"""
import argparse
import glob
import json
import os


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--meta_dir", required=True, help="Directory of metadata file")
    argparser.add_argument("--candidate", type=str, default="./multidomain2langs.json", help="Candidate file path")
    argparser.add_argument("--out_path", type=str, default="./urls_tocrawl.txt", help="Urls output path")
    argparser.add_argument("--langs", type=str, nargs=2, help="three-letter language codes")
    args = argparser.parse_args()

    meta_files = glob.glob(os.path.join(args.meta_dir, "*.meta"))

    with open(args.candidate, encoding="utf-8") as stream:
        multidomain2langs = json.load(stream)

    urls = set()
    lang1, lang2 = args.langs

    urls_found = 0

    for f in meta_files:
        print("Getting urls from metadata file ", f)
        report_interval = 20000
        total = 0

        with open(f, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                url, host, domain, lang, content_len = parts

                if domain in multidomain2langs:
                    langs = multidomain2langs[domain]
                    if lang1 in langs and lang2 in langs:
                        urls.add(url)
                        urls_found += 1

                total += 1
                if total % report_interval == 0:
                    print(total, urls_found)
            print(total, urls_found)

    with open(args.out_path, "w", encoding="utf-8") as stream:
        for url in urls:
            stream.write(url + "\n")
