"""Extract OPUS zip files"""
import argparse

from yimt_bitext.opus.utils import extract_zips
from yimt_bitext.utils.log import get_logger

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--in_dir", type=str, required=True, help="zip file dir")
    argparser.add_argument("--out_dir", type=str, default=None, help="output dir")
    args = argparser.parse_args()

    logger = get_logger("./log.txt", "corpus")

    extract_zips(args.in_dir, args.out_dir, logger_opus=logger)
