import argparse

from yimt_bitext.dedup.dedup import norm
from yimt_bitext.utils.log import get_logger


def diff_tsv(tsv_file1, tsv_file2, out_file=None, creterion="SRC",
             lower=True, remove_noletter=True,
             logger=None):
    if out_file is None:
        out_file = tsv_file1 + ".diff"
    pairs = set()
    srcs = set()
    tgts = set()
    total = 0

    if logger:
        logger.info("Scanning {}...".format(tsv_file2))
    with open(tsv_file2, encoding="utf-8") as bf:
        for p in bf:
            total += 1
            if total % 100000 == 0:
                if logger:
                    logger.info("{}".format(total))
            p = p.strip()
            pp = p.split("\t")
            if len(pp) != 2:
                continue
            src = pp[0].strip()
            tgt = pp[1].strip()
            src = norm(src, lower, remove_noletter)
            hs = hash(src)
            srcs.add(hs)

            tgt = norm(tgt, lower, remove_noletter)
            ht = hash(tgt)
            tgts.add(ht)

            p = norm(p, lower, remove_noletter)
            h = hash(p)
            pairs.add(h)

    if logger:
        logger.info("{}".format(total))

    differed = 0
    total = 0

    if logger:
        logger.info("Scanning {}...".format(tsv_file1))
    with open(tsv_file1, encoding="utf-8") as f, open(out_file, "w", encoding="utf-8") as out_f:
        for p in f:
            p = p.strip()
            total += 1
            if total % 100000 == 0:
                if logger:
                    logger.info("Total: {}, Diff: {}".format(total, differed))

            if creterion == "SRC" or creterion == "TGT":
                pp = p.split("\t")
                if len(pp) != 2:
                    continue
                src = pp[0].strip()
                tgt = pp[1].strip()
                if creterion == "SRC":
                    src = norm(src, lower, remove_noletter)
                    hs = hash(src)
                    if hs not in srcs:
                        out_f.write(p + "\n")
                        differed += 1
                else:
                    tgt = norm(tgt, lower, remove_noletter)
                    ht = hash(tgt)
                    if ht not in tgts:
                        out_f.write(p + "\n")
                        differed += 1
            else:
                pn = norm(p, lower, remove_noletter)
                h = hash(pn)
                if h not in pairs:
                    out_f.write(p + "\n")
                    differed += 1

    if logger:
        logger.info("Total: {}, Diff: {}".format(total, differed))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="C1-C2")
    parser.add_argument("-i1", "--input1", required=True, help="input file1")
    parser.add_argument("-i2", "--input2", required=True, help="input file2")
    parser.add_argument("-o", "--output", required=True, help="output file")
    args = parser.parse_args()

    logger = get_logger("./log.txt", "corpus")

    diff_tsv(args.input1, args.input2, args.output, creterion="SRC", logger=logger)
