import argparse

from yimt_bitext.opus.utils import filter_tsv
from yimt_bitext.utils.log import get_logger


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--input", required=True, help="Bitext file with scores")
    argparser.add_argument("-o", "--output", default=None, help="output file")
    argparser.add_argument("--min", default=0.66, type=float, help="Min socre for bitext")
    args = argparser.parse_args()

    in_path = args.input
    out_path = args.output
    if out_path is None:
        out_path = in_path + ".sf"
    min_score = args.min

    logger = get_logger("./log.txt", "corpus")

    filter_tsv(in_path, out_path, min_score, logger=logger)
