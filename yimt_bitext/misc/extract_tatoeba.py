import argparse


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--input", required=True, help="Input file path")
    argparser.add_argument("-o", "--output", required=True, help="Output file path")
    argparser.add_argument("-sl", "--source_langs", nargs="*", help="Choose lines with these source languages")
    argparser.add_argument("-tl", "--target_langs", nargs="*", help="Choose lines with these target languages")
    args = argparser.parse_args()
    in_fn = args.input
    out_fn = args.output

    tgt_lang = args.target_langs  # ["cmn_Hans", "cmn_Hant"]
    src_lang = args.source_langs

    outf = open(out_fn, "w", encoding="utf-8")

    with open(in_fn, encoding="utf-8") as inf:
        for line in inf:
            line = line.strip()
            segs = line.split("\t")

            if tgt_lang is not None and segs[1] not in tgt_lang:
                continue

            if src_lang is not None and segs[0] not in src_lang:
                continue

            outf.write(segs[2] + "\t" + segs[3] + "\n")

    outf.close()
