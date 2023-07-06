import os
from argparse import ArgumentParser
from pathlib import Path

from yimt_bitext.opus.utils import extract_zips, merge_moses, merge
from yimt_bitext.utils.dedup import dedup_bitext_file
from yimt_bitext.utils.filters import filter_file, EmptyFilter, SameFilter, OverlapFilter, NonZeroNumeralsFilter, \
    AlphabetRatioFilter, RepetitionFilter, CharacterRatioFilter, get_lang2script
from yimt_bitext.utils.log import get_logger
from yimt_bitext.utils.normalizers import ToZhNormalizer, normalize_file

lang2script = get_lang2script()


def ndf_dir(in_dir, target_lang="zh",
            clean_after_done=False,
            logger=None):
    logger.info("Preprocessing {}".format(in_dir))

    logger.info("***Unzipping***")
    path = extract_zips(in_dir, logger_opus=logger)

    logger.info("***Merging Moses***")
    path = merge_moses(path, target_lang=target_lang, clean_after_merge=clean_after_done, logger_opus=logger)

    logger.info("***Merging Files***")
    parts = Path(in_dir).parts
    dirname = parts[-1]
    path = merge(path, os.path.join(path, dirname + ".tsv"), clean_after_merge=clean_after_done, logger_opus=logger)

    logger.info("***Normalizing***")
    normalizers = []
    if target_lang == "zh":
        normalizers = [ToZhNormalizer()]
    path = normalize_file(path, normalizers, clean_after_done=clean_after_done, logger=logger)

    logger.info("***Deduping***")
    path = dedup_bitext_file(path, dedup_srctgt=False, dedup_src=True, dedup_tgt=False,
                             remove_noletter=False, clean_after_done=clean_after_done, logger=logger)

    logger.info("***Filtering***")
    filters = [EmptyFilter(), SameFilter(), OverlapFilter(ratio=0.80), NonZeroNumeralsFilter(threshold=1.0),
               AlphabetRatioFilter(threshold=0.33, exclude_whitespace=True), RepetitionFilter()]
    langs = dirname.split("-")
    if len(langs) == 2:
        sl, tl = langs
        src_script = lang2script[sl]
        tgt_script = lang2script[tl]
        char_filter = CharacterRatioFilter(scripts=(src_script, tgt_script), thresholds=(0.33, 0.33))
        filters.append(char_filter)

    path = filter_file(path, filters=filters, clean_after_done=clean_after_done, logger=logger)

    return path


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--root", help="Root dir")
    argparser.add_argument("--tl", default="zh", help="target language")
    argparser.add_argument("--log_dir", default="./", help="log directory")
    args = argparser.parse_args()

    logger_opus = get_logger(os.path.join(args.log_dir, "opus.log"), "OPUS")

    root = args.root

    ndf_dir(root, clean_after_done=False, logger=logger_opus)
