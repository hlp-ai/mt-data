"""Tokenize file with SentencePiece"""
import argparse

from yimt_bitext.utils.sp import tokenize_file, load_spm

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--sp_model", required=True, help="SentencePiece model path")
    argparser.add_argument("--in_fn", required=True, help="Corpus file path")
    argparser.add_argument("--out_fn", default=None, help="Ouput file path")
    args = argparser.parse_args()

    if args.out_fn is None:
        out_fn = args.in_fn + ".tok"
    else:
        out_fn = args.out_fn

    sp = load_spm(args.sp_model)
    tokenize_file(sp, args.in_fn, out_fn)
