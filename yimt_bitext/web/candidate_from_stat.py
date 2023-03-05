"""3. Output bilingual hosts/domains based on stat data"""
import argparse
import json
import os

from yimt_bitext.web.cc import update_k2set

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--stat_path", type=str, required=True, help="stat file")
    args = argparser.parse_args()

    stat_path = args.stat_path
    multihost2langs_path = os.path.join(os.path.dirname(stat_path), "multihost2langs.json")

    host2lang2len = {}
    print("Loading stat file...")
    with open(stat_path, encoding="utf-8") as f:
        host2lang2len = json.load(f)

    print("# network loc: ", len(host2lang2len))

    multihost2langs = {}
    if os.path.exists(multihost2langs_path):
        print("Loading stat file for updating...")
        with open(multihost2langs_path, encoding="utf-8") as f:
            multihost2langs = json.load(f)

    for netloc, lang2len in host2lang2len.items():
        # TODO: judgement by ratio of lengths of text of different languages
        if len(lang2len) >= 2:
            for lang, txt_len in lang2len.items():
                update_k2set(multihost2langs, netloc, lang)

    with open(multihost2langs_path, "w", encoding="utf-8") as stream:
        json.dump(multihost2langs, stream)

    print("# of multilingual host:", len(multihost2langs))