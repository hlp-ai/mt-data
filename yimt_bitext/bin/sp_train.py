"""Train SentencePiece model from corpus"""
import argparse

from yimt_bitext.utils.sp import train_spm

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--corpus", required=True, help="Corpus file path")
    argparser.add_argument("--sp_prefix", default=None, help="SentencePiece model path prefix")
    argparser.add_argument("--vocab_size", type=int, default=32000, help="Vocab size")
    argparser.add_argument("--max_sentences", type=int, default=5000000, help="Max number of sentences for training")
    argparser.add_argument("--coverage", type=float, default=0.9999, help="Vocab coverage")
    argparser.add_argument("--custom_symbol_file", default=None, help="user defined symbols file")
    args = argparser.parse_args()

    if args.sp_prefix is None:
        sp_prefix = "{}-sp-{}".format(args.corpus, args.vocab_size)
    else:
        sp_prefix = args.sp_prefix

    user_defined_symbols =  args.custom_symbol_file

    train_spm(args.corpus, sp_prefix, args.vocab_size,
              coverage=args.coverage, num_sentences=args.max_sentences,
              user_defined_symbols_file=user_defined_symbols)
