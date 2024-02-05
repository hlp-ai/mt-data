import os
from argparse import ArgumentParser

from yimt_bitext.dedup.dedup import dedup_tsv_file
from yimt_bitext.filter.filters import get_lang2script, EmptyFilter, SameFilter, OverlapFilter, AlphabetRatioFilter, \
    RepetitionFilter, CharacterRatioFilter, filter_file
from yimt_bitext.normalize.normalizers import ToZhNormalizer, normalize_file
from yimt_bitext.utils.log import get_logger


lang2script = get_lang2script()


def preprocess_file_ndf(in_file,
                        source_lang, target_lang="zh",
               clean_after_done=False,
               logger=None):
    logger.info("Preprocessing {}".format(in_file))

    logger.info("***Normalizing***")
    normalizers = []
    if target_lang == "zh":
        normalizers = [ToZhNormalizer()]
    path = normalize_file(in_file, normalizers, clean_after_done=clean_after_done, logger=logger)

    logger.info("***Deduping***")
    path = dedup_tsv_file(path, dedup_srctgt=False, dedup_src=True, dedup_tgt=False,
                          remove_noletter=False, clean_after_done=clean_after_done, logger=logger)

    logger.info("***Filtering***")
    filters = [EmptyFilter(), SameFilter(), OverlapFilter(ratio=0.80),
               AlphabetRatioFilter(threshold=0.33, exclude_whitespace=True), RepetitionFilter()]
    src_script = lang2script[source_lang]
    tgt_script = lang2script[target_lang]
    char_filter = CharacterRatioFilter(scripts=(src_script, tgt_script), thresholds=(0.33, 0.33))
    filters.append(char_filter)

    path = filter_file(path, filters=filters, clean_after_done=clean_after_done, logger=logger)

    return path


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--input", required=True, help="input tsv file")
    argparser.add_argument("--sl", required=True, help="source language")
    argparser.add_argument("--tl", default="zh", help="target language")
    argparser.add_argument("--log_dir", default="./", help="log directory")
    args = argparser.parse_args()

    logger_opus = get_logger(os.path.join(args.log_dir, "opus.log"), "OPUS")

    in_file = args.input
    source_lang = args.sl
    target_lang = args.tl

    preprocess_file_ndf(in_file, source_lang, clean_after_done=False, logger=logger_opus)
