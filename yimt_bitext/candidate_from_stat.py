"""3. Output bilingual hosts/domains based on stat data"""
import argparse
import json

from yimt_bitext.cc import update_k2set

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--stat_path", type=str, required=True, help="stat file")
    argparser.add_argument("--out_path", type=str, default="./multidomain2langs.json", help="output file path")
    args = argparser.parse_args()

    stat_path = args.stat_path
    output_path = args.out_path

    with open(stat_path, encoding="utf-8") as f:
        print("Loading stat file...")
        domain2lang2len = json.load(f)

    print("# network loc: ", len(domain2lang2len))

    multidomain2langs = {}

    with open(output_path, "a", encoding="utf-8") as f:
        for netloc, lang2len in domain2lang2len.items():
            # TODO: judgement by ratio of lengths of text of different languages
            if len(lang2len) >= 2:
                for lang, txt_len in lang2len.items():
                    update_k2set(multidomain2langs, netloc, lang)

    with open(output_path, "w", encoding="utf-8") as stream:
        json.dump(multidomain2langs, stream)

    print("# of multilingual domain:", len(multidomain2langs))