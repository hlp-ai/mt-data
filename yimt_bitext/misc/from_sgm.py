"""Convert sgm file of WMT into plain text"""
import argparse
import io
import re


def from_sgm(sgm_path, out_path):
    """Convert sgm file of WMT into plain text"""
    pattern = re.compile(r"<seg id=\"\d+\">(.+?)</seg>")

    lines = "\r".join(io.open(sgm_path, encoding="utf-8").readlines())

    out_f = io.open(out_path, "w", encoding="utf-8")

    for m in re.finditer(pattern, lines):
        print(m.group(1))
        out_f.write(m.group(1) + "\n")

    out_f.close()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", type=str, required=True, help="input file")
    argparser.add_argument("--output", type=str, required=True, help="output file")
    args = argparser.parse_args()

    corpus_fn = args.input
    out_fn = args.output

    from_sgm(corpus_fn, out_fn)
