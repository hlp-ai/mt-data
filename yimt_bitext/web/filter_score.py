import argparse


def filter(in_path, out_path, min_score):
    with open(in_path, encoding="utf-8") as in_f, open(out_path, "w", encoding="utf-8") as out_f:
        for line in in_f:
            line = line.strip()
            parts = line.split("\t")
            if len(parts) != 3:
                continue

            if float(parts[0]) > min_score:
                out_f.write(parts[1] + "\t" + parts[2] + "\n")


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", required=True, help="Bitext file with scores")
    argparser.add_argument("--out", default=None, help="output file")
    argparser.add_argument("--min", default=0.66, type=float, help="Min socre for bitext")
    args = argparser.parse_args()

    in_path = args.input
    out_path = args.out
    if out_path is None:
        out_path = in_path + ".sf"
    min_score = args.min

    filter(in_path, out_path, min_score)
