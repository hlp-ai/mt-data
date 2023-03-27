"""4. Get entries to crawl from candidate multilingual hosts"""
import argparse
import json
import os


def get_multilang_site(site2langs, langs):
    multisite2langs_fn = site2langs
    with open(multisite2langs_fn, encoding="utf-8") as stream:
        multisite2langs = json.load(stream)

    lang1, lang2 = langs
    entries_path = os.path.join(os.path.dirname(multisite2langs_fn), "entries_tocrawl-" + "-".join(langs) + ".txt")

    entries = set()
    if os.path.exists(entries_path):
        print("Loading entries for updating...")
        with open(entries_path, encoding="utf-8") as f:
            for entry in f:
                entries.add(entry.strip())

    print("# of entries found:", len(entries))

    entries_found = 0
    report_interval = 2000
    total = 0

    for host, langs in multisite2langs.items():
        if lang1 in langs and lang2 in langs and host not in entries:
            entries.add(host)
            entries_found += 1

        total += 1
        if total % report_interval == 0:
            print("{} entries scanned, {} new multilingual entries found".format(total, entries_found))
    print("{} entries scanned, {} new multilingual entries found".format(total, entries_found))

    with open(entries_path, "w", encoding="utf-8") as stream:
        for url in entries:
            stream.write(url + "\n")


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--site2langs", type=str, required=True, help="site-to-langs file")
    argparser.add_argument("--langs", type=str, nargs=2, required=True, help="three-letter language codes")
    args = argparser.parse_args()

    get_multilang_site(args.site2langs, args.langs)
