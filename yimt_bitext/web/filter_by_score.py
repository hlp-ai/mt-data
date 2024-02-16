"""7. 对句对打分文件进行阈值过滤，并从过滤后的结果中选择最高得分的句对"""
import argparse
import os

from yimt_bitext.utils.log import get_logger


def filter_score(in_path, out_path=None, min_score=0.60, logger=None):
    if out_path is None:
        out_path = in_path + ".sfilter"

    total = 0
    left = 0
    with open(in_path, encoding="utf-8") as in_f, open(out_path, "w", encoding="utf-8") as out_f:
        for line in in_f:
            total += 1
            if total % 100000 == 0:
                if logger:
                    logger.info("Total: {}, Left: {}".format(total, left))
            line = line.strip()
            parts = line.split("\t")
            if len(parts) != 3:
                continue

            if float(parts[0]) > min_score:
                out_f.write(parts[0] + "\t" + parts[1] + "\t" + parts[2] + "\n")
                left += 1

    if logger:
        logger.info("Total: {}, Left: {}".format(total, left))

    return out_path


def filter_max(in_path, out_path=None, logger=None):
    if out_path is None:
        out_path = in_path + ".sfilter"

    total = 0
    left = 0
    pairs = []
    with open(in_path, encoding="utf-8") as in_f:
        for line in in_f:
            total += 1
            if total % 100000 == 0:
                if logger:
                    logger.info("Total: {}".format(total))
            line = line.strip()
            parts = line.split("\t")
            if len(parts) != 3:
                continue

            pairs.append((parts[1], parts[0], parts[2]))

    if logger:
        logger.info("Total: {}".format(total))

    with open(out_path, "w", encoding="utf-8") as out_f:
        src = ""
        for e in sorted(pairs, reverse=True):
            # print(e)
            if e[0] != src:
                out_f.write(e[0] + "\t" + e[2] + "\n")
                src = e[0]
                left += 1

    if logger:
        logger.info("Total: {}, Left: {}".format(total, left))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Filter corpus based on score")
    argparser.add_argument("-i", "--input", required=True, help="Bitext file with scores")
    argparser.add_argument("-o", "--output", default=None, help="output file")
    argparser.add_argument("--min", default=0.66, type=float, help="Min socre for bitext")
    argparser.add_argument("--log_dir", default="./", help="log directory")
    args = argparser.parse_args()

    in_path = args.input
    out_path = args.output
    if out_path is None:
        out_path = in_path + ".sf"
    min_score = args.min

    logger = get_logger(os.path.join(args.log_dir, "opus.log"), "OPUS")

    logger.info("Filtering pairs by score...")
    p = filter_score(in_path, out_path, min_score, logger=logger)

    logger.info("Selecting pairs with max score...")
    filter_max(p, logger=logger)
