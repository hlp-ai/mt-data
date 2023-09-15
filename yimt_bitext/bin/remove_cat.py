import sys


def strip_cat(in_fn, out_fn=None):
    if out_fn is None:
        out_fn = in_fn + ".de"

    with open(in_fn, encoding="utf-8") as f, open(out_fn, "w", encoding="utf-8") as out:
        for line in f:
            line = line.strip()
            pars = line.split("\t")
            out.write(pars[0] + "\t" + pars[1] + "\n")


if __name__ == "__main__":
    inp = sys.argv[1]
    out = None
    if len(sys.argv) > 2:
        out = sys.argv[2]
    strip_cat(inp, out)
