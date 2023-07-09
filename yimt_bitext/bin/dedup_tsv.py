"""Delete duplicate pairs from parallel corpus"""
import argparse

from yimt_bitext.utils.dedup import dedup_bitext_file
from yimt_bitext.utils.log import get_logger

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--input", type=str, required=True, help="input file")
    argparser.add_argument("-o", "--output", default=None, help="output file")
    argparser.add_argument("-s", "--dedup_src", action="store_true", help="dedup based on source")
    argparser.add_argument("-t", "--dedup_tgt", action="store_true", help="dedup based on target")
    argparser.add_argument("-st", "--dedup_srctgt", action="store_true", help="dedup based on source and target")
    args = argparser.parse_args()

    corpus_fn = args.input
    out_fn = args.output

    logger = get_logger("./log.txt", "corpus")

    logger.info("SRC: {}, TGT: {}， SRC_TGT: {}".format(args.dedup_src, args.dedup_tgt, args.dedup_srctgt))

    if args.dedup_srctgt or args.dedup_src or args.dedup_tgt:
        dedup_bitext_file(corpus_fn, out_fn, args.dedup_src, args.dedup_tgt, args.dedup_srctgt, logger=logger)
    else:
        print("Missing dedup condition.")
