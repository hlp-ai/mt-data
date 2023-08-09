"""Split TSV file into source and target file"""
import argparse

from yimt_bitext.opus.utils import pair_to_single


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("tsv_fn")
    argparser.add_argument("src_fn")
    argparser.add_argument("tgt_fn")
    args = argparser.parse_args()

    pair_fn = args.tsv_fn
    src_fn = args.src_fn
    tgt_fn = args.tgt_fn

    pair_to_single(pair_fn, src_fn, tgt_fn)


