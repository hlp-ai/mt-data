"""Detokenize file into file"""
import argparse

from yimt_bitext.split.sp import detokenize_file, load_spm

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("sp_model")
    argparser.add_argument("in_fn")
    argparser.add_argument("out_fn")
    args = argparser.parse_args()

    sp = load_spm(args.sp_model)
    detokenize_file(sp, args.in_fn, args.out_fn)
