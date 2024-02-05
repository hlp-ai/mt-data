"""对打分TSV平行语料文件进行过滤"""
import argparse
import os

from yimt_bitext.utils.log import get_logger


def filter_tsv_score(in_path, out_path=None, min_score=0.60, logger=None):
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
                out_f.write(parts[1] + "\t" + parts[2] + "\n")
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

    logger_opus = get_logger(os.path.join(args.log_dir, "opus.log"), "OPUS")

    filter_tsv_score(in_path, out_path, min_score, logger=logger_opus)
