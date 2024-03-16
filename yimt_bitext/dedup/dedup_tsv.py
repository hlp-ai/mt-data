"""平行语料去重"""
import argparse

from yimt_bitext.dedup.dedup import dedup_tsv_file
from yimt_bitext.utils.log import get_logger

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--input", type=str, required=True, help="input file")
    argparser.add_argument("-o", "--output", default=None, help="output file")
    argparser.add_argument("-s", "--dedup_src", action="store_true", help="dedup based on source")
    argparser.add_argument("-t", "--dedup_tgt", action="store_true", help="dedup based on target")
    argparser.add_argument("-st", "--dedup_srctgt", action="store_true", help="dedup based on source and target")
    argparser.add_argument("--noletter", action="store_true", help="remove noletter")
    args = argparser.parse_args()

    corpus_fn = args.input
    out_fn = args.output

    logger = get_logger("./log.txt", "Dedup")

    if args.dedup_srctgt or args.dedup_src or args.dedup_tgt:
        dedup_tsv_file(corpus_fn, out_fn, args.dedup_src, args.dedup_tgt, args.dedup_srctgt,
                       logger=logger, remove_noletter=args.noletter)
    else:
        print("Missing dedup condition.")
