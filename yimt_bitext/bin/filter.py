import argparse

from yimt_bitext.utils.filters import get_lang2script, filter_file, EmptyFilter, SameFilter, OverlapFilter, \
    NonZeroNumeralsFilter, RepetitionFilter, AlphabetRatioFilter, CharacterRatioFilter, LengthFilter
from yimt_bitext.utils.log import get_logger


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", required=True, help="Input file path")
    argparser.add_argument("--output", default=None, help="Ouput file path")
    argparser.add_argument("--lang_pair", required=True, help="Language pair")
    args = argparser.parse_args()

    logger = get_logger("./log.txt", "corpus")

    filters = [EmptyFilter(), SameFilter(), OverlapFilter(ratio=0.80), NonZeroNumeralsFilter(threshold=1.0),
               AlphabetRatioFilter(threshold=0.33, exclude_whitespace=True), RepetitionFilter()]

    lang2script = get_lang2script()

    lang_pair = args.lang_pair
    sl, tl = lang_pair.split("-")
    src_script = lang2script[sl]
    tgt_script = lang2script[tl]
    char_filter = CharacterRatioFilter(scripts=(src_script, tgt_script), thresholds=(0.33, 0.33))
    filters.append(char_filter)

    if tl == "en":
        tgt_len = LengthFilter.space_sep_len_f
        filters.append(LengthFilter(tgt_len_fn=tgt_len, tgt_lens=(1, 128)))

    filter_file(args.input, filters=filters, out_path=args.output, logger=logger)
