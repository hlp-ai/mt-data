"""对TSV平行语料进行过滤"""
import argparse
import os

from yimt_bitext.filter.filters import load_filters
from yimt_bitext.utils.log import get_logger


def filter_file(in_path, filters, out_path=None, clean_after_done=False, logger=None):
    if logger:
        logger.info(filters)

    if out_path is None:
        out_path = in_path + ".filtered"

    if os.path.exists(out_path):
        logger.info("{} exists".format(out_path))
        return out_path

    total = 0
    passed = 0

    with open(in_path, encoding="utf-8") as in_f, open(out_path, "w", encoding="utf-8") as out_f:
        for line in in_f:
            total += 1
            if total % 100000 == 0:
                if logger:
                    logger.info("Total: {} Passed: {}".format(total, passed))
            line = line.strip()
            cols = line.split("\t")
            if len(cols) >= 2:
                src, tgt = cols[:2]
            else:
                if logger:
                    logger.warning("NO Pair: {}".format(line))
                continue

            valid = True
            for f in filters:
                if f.filter(src, tgt) is None:
                    if logger:
                        logger.debug("{}: {}".format(f.__class__.__name__, line))
                    valid = False
                    break
            if valid:
                passed += 1
                out_f.write(line + "\n")

    if logger:
        logger.info("Total: {} Passed: {}".format(total, passed))

    if clean_after_done:
        os.remove(in_path)

    return out_path


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--input", required=True, help="Input file path")
    argparser.add_argument("-o", "--output", default=None, help="Ouput file path")
    argparser.add_argument("-c", "--config", required=True, help="Filter config file")
    args = argparser.parse_args()

    logger = get_logger("./log.txt", "Filter")

    filters = load_filters(args.config)

    filter_file(args.input, filters=filters, out_path=args.output, logger=logger)
