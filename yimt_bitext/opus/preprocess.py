import os
import shutil
import sys
from pathlib import Path

from yimt_bitext.opus.utils import extract_zips, merge_moses, merge_files, split
from yimt_bitext.utils.dedup import dedup_bitext_file
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
    parts = Path(in_dir).parts
    dirname = parts[-1]
    path = merge_files(path, dirname + ".tsv", logger_opus=logger)

    logger.info("***Normalizing***")
    normalizers = []
    if target_lang == "zh":
        normalizers = [ToZhNormalizer()]
    path = normalize_file(path, normalizers, logger=logger)

    logger.info("***Deduping***")
    path = dedup_bitext_file(path, dedup_srctgt=True, remove_noletter=False, logger=logger)

    logger.info("***Filtering***")
    filters = [EmptyFilter(), SameFilter(), OverlapFilter(ratio=0.5), NonZeroNumeralsFilter(threshold=1.0),
               AlphabetRatioFilter(threshold=0.75, exclude_whitespace=True), RepetitionFilter()]
    path = filter_file(path, filters=filters, logger=logger)

    logger.info("***Splitting***")
    split_dir = os.path.join(os.path.dirname(path), "score")
    os.mkdir(split_dir)
    path = shutil.copy(path, split_dir)
    split(path, logger=logger)

    return path


if __name__ == "__main__":
    p = sys.argv[1]
    logger_opus = get_logger("opus.log", "OPUS")
    preprocess(p, logger=logger_opus)