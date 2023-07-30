import argparse
import os

from yimt_bitext.opus.utils import filter_tsv
from yimt_bitext.utils.log import get_logger


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Filter corpus based on score")
    argparser.add_argument("-i", "--input", required=True, help="input directory")
    argparser.add_argument("--min", default=0.66, type=float, help="Min socre for bitext")
    argparser.add_argument("--log_dir", default="./", help="log directory")
    args = argparser.parse_args()

    in_path = args.input
    min_score = args.min

    logger_opus = get_logger(os.path.join(args.log_dir, "opus.log"), "OPUS")

    filter_dir = os.path.join(in_path, "sfilter")
    if not os.path.exists(filter_dir):
        os.mkdir(filter_dir)
    else:
        logger_opus.info("{} exists".format(filter_dir))

    files = os.listdir(in_path)
    for f in files:
        if f.endswith(".score"):
            logger_opus.info("Filter {} by score".format(f))
            out_path = os.path.join(filter_dir, f + ".sfilter")
            if os.path.exists(out_path):
                logger_opus.info("{} exists".format(out_path))
                continue

            filter_tsv(os.path.join(in_path, f), out_path, min_score, logger=logger_opus)
