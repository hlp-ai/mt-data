"""3. Output bilingual hosts/domains based on stat data"""
import argparse
import json

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--stat_path", type=str, required=True, help="stat file")
    argparser.add_argument("--langs", type=str, nargs=2, help="two three-letter language codes")
    argparser.add_argument("--out_path", type=str, default="./candidates.txt", help="output file path")
    args = argparser.parse_args()

    stat_path = args.stat_path
    output_path = args.out_path

    with open(stat_path, encoding="utf-8") as f:
        print("Loading stat file...")
        stats = json.load(f)

    candidates = set()

    print("# network loc: ", len(stats))

    lang1, lang2 = args.langs

    new_biling_netlocs = 0

    with open(output_path, "a", encoding="utf-8") as f:
        for netloc, lang2len in stats.items():
            if netloc in candidates:
                continue
            # TODO: judgement by ratio of lengths of text of different languages
            if lang1 in lang2len and lang2 in lang2len:
                f.write(netloc + "\n")
                new_biling_netlocs += 1

    print("# of new candidate bilingual netlocs found: ", new_biling_netlocs)
