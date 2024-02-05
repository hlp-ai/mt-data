import argparse


def add_token(tsv_file, add_src, token):
    out_file = tsv_file + ".addtoken"
    with open(tsv_file, encoding="utf-8") as raw, open(out_file, "w", encoding="utf-8") as out:
        for line in raw:
            parts = line.strip().split("\t")
            if len(parts) != 2:
                continue

            src, tgt = parts
            if add_src:
                src = token + src
            else:
                tgt = token + tgt

            out.write(src + "\t" + tgt + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tsv_file", required=True, help="tsv file")
    parser.add_argument("--to", default="src", type=str, help="src or tgt")
    parser.add_argument("--token", required=True, help="token to add")
    args = parser.parse_args()

    input = args.tsv_file
    tosrc = True
    if args.to == "tgt":
        tosrc = False

    add_token(input, tosrc, args.token)