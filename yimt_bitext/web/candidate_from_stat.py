"""3. Output bilingual hosts/domains based on stat data"""
import argparse
import json
import os

from yimt_bitext.web.cc import update_k2set


def gen_candidate_multilang_site(stat_path):
    multisite2langs_path = os.path.join(os.path.dirname(stat_path), "multisite2langs.json")

    print("Loading stat file...")
    with open(stat_path, encoding="utf-8") as f:
        site2lang2len = json.load(f)

    print("# network loc: ", len(site2lang2len))

    multisite2langs = {}
    if os.path.exists(multisite2langs_path):
        print("Loading stat file for updating...")
        with open(multisite2langs_path, encoding="utf-8") as f:
            multisite2langs = json.load(f)

    for netloc, lang2len in site2lang2len.items():
        # TODO: judgement by ratio of lengths of text of different languages
        if len(lang2len) >= 2:
            for lang, txt_len in lang2len.items():
                update_k2set(multisite2langs, netloc, lang)

    with open(multisite2langs_path, "w", encoding="utf-8") as stream:
        json.dump(multisite2langs, stream)

    print("# of multilingual site:", len(multisite2langs))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--stat_path", type=str, required=True, help="stat file")
    args = argparser.parse_args()

    stat_path = args.stat_path
    gen_candidate_multilang_site(stat_path)
