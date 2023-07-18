import argparse

from yimt_bitext.opus.utils import merge_moses
from yimt_bitext.utils.log import get_logger

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--in_dir", type=str, required=True, help="input dir")
    argparser.add_argument("--out_dir", type=str, default=None, help="output dir")
    argparser.add_argument("--src_lang", type=str, default=None, help="source language")
    argparser.add_argument("--tgt_lang", type=str, default=None, help="target language")
    args = argparser.parse_args()

    logger = get_logger("./log.txt", "corpus")

    merge_moses(args.in_dir, args.src_lang, args.tgt_lang, args.out_dir, logger_opus=logger)
