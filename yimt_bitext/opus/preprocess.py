import sys

from yimt_bitext.opus.utils import extract_zips, merge_moses, merge_files
from yimt_bitext.utils.dedup import dedup_file
from yimt_bitext.utils.filters import filter_file, EmptyFilter, SameFilter, OverlapFilter, NonZeroNumeralsFilter, \
    AlphabetRatioFilter, RepetitionFilter
from yimt_bitext.utils.log import get_logger
from yimt_bitext.utils.normalizers import ToZhNormalizer, normalize_file


def preprocess(in_dir, target_lang="zh", logger=None):
    logger.info("***Unzipping***")
    path = extract_zips(in_dir, logger_opus=logger)

    logger.info("***Merging Moses***")
    path = merge_moses(path, target_lang=target_lang, logger_opus=logger)

    logger.info("***Merging Files***")
    path = merge_files(path, "to" + target_lang + ".tsv", logger_opus=logger)

    logger.info("***Normalizing***")
    if target_lang == "zh":
        normalizers = [ToZhNormalizer()]
    path = normalize_file(path, normalizers, logger=logger)

    logger.info("***Deduping***")
    path = dedup_file(path, logger=logger)

    logger.info("***Filtering***")
    filters = [EmptyFilter(), SameFilter(), OverlapFilter(ratio=0.5), NonZeroNumeralsFilter(threshold=1.0),
               AlphabetRatioFilter(threshold=0.75), RepetitionFilter()]
    filter_file(path, filters=filters, logger=logger)


if __name__ == "__main__":
    p = sys.argv[1]
    logger_opus = get_logger("opus.log", "OPUS")
    preprocess(p, logger=logger_opus)