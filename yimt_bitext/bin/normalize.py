"""Normalize bitext"""
import argparse

from yimt_bitext.utils.log import get_logger
from yimt_bitext.utils.normalizers import normalize_file, ToZhNormalizer, CleanerTSV

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", required=True, help="Input file path")
    argparser.add_argument("--output", default=None, help="Ouput file path")
    argparser.add_argument("--tgt_lang", default="zh", help="Target language")
    args = argparser.parse_args()

    logger = get_logger("./log.txt", "corpus")

    if args.tgt_lang == "zh":
        normalizers = [ToZhNormalizer()]
    else:
        normalizers = [CleanerTSV()]

    normalize_file(args.input, normalizers, out_path=args.output, logger=logger)
