import os
import re
import shutil
from argparse import ArgumentParser
from pathlib import Path

from yimt_bitext.opus.utils import extract_zips, merge_moses, merge_files, split, score_tsv
from yimt_bitext.utils.dedup import dedup_bitext_file
from yimt_bitext.utils.filters import filter_file, EmptyFilter, SameFilter, OverlapFilter, NonZeroNumeralsFilter, \
    AlphabetRatioFilter, RepetitionFilter, CharacterRatioFilter, get_lang2script
from yimt_bitext.utils.log import get_logger
from yimt_bitext.utils.normalizers import ToZhNormalizer, normalize_file
from yimt_bitext.web.filter_score import filter_tsv


lang2script = get_lang2script()


def preprocess_dir(in_dir, target_lang="zh",
               labse_model_dir="D:/kidden/mt/open/mt-ex/mt/data/labse1",
               block=8,
               min_socre=0.6,
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
    path = merge_files(path, dirname + ".tsv", clean_after_merge=clean_after_done, logger_opus=logger)

    logger.info("***Normalizing***")
    normalizers = []
    if target_lang == "zh":
        normalizers = [ToZhNormalizer()]
    path = normalize_file(path, normalizers, clean_after_done=clean_after_done, logger=logger)

    logger.info("***Deduping***")
    path = dedup_bitext_file(path, dedup_srctgt=True, dedup_src=False, dedup_tgt=False,
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

    logger.info("***Splitting***")
    split_dir = os.path.join(os.path.dirname(path), "score")
    if not os.path.exists(split_dir):
        os.mkdir(split_dir)
        path = shutil.move(path, split_dir)
        split(path, logger=logger)

    logger.info("***Scoring***")
    files = os.listdir(split_dir)
    for f in files:
        if re.match(r".+\d+$", f):
            score_tsv(os.path.join(split_dir, f),
                      labse_model_dir=labse_model_dir,
                      block=block, clean_after_done=clean_after_done, logger=logger)

    logger.info("***Filtering by score***")
    filter_dir = os.path.join(split_dir, "sfilter")
    if not os.path.exists(filter_dir):
        os.mkdir(filter_dir)
    files = os.listdir(split_dir)
    for f in files:
        if f.endswith(".score"):
            logger.info("Filter {} by score".format(f))
            out_path = os.path.join(filter_dir, f+".sfilter")
            if os.path.exists(out_path):
                continue
            filter_tsv(os.path.join(split_dir, f), out_path, min_socre, logger=logger)

    logger.info("***Merging Files***")
    out_path = os.path.join(filter_dir, dirname + "-preprocessed.tsv")
    if not os.path.exists(out_path):
        path = merge_files(filter_dir, out_path, clean_after_merge=clean_after_done, logger_opus=logger)

    return path


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--root", help="Root dir")
    argparser.add_argument("--tl", default="zh", help="target language")
    argparser.add_argument("--labse", default="D:/kidden/mt/open/mt-ex/mt/data/labse1", help="directory for labse")
    argparser.add_argument("--block", type=int, default=8, help="block size for labse")
    argparser.add_argument("--min", type=float, default=0.6, help="min socre for filtering")
    argparser.add_argument("--log_dir", default="./", help="log directory")
    args = argparser.parse_args()

    logger_opus = get_logger(os.path.join(args.log_dir, "opus.log"), "OPUS")

    root = args.root
    sub = os.listdir(root)
    contain_langs = all([os.path.isdir(os.path.join(root,d)) for d in sub])
    if not contain_langs:
        preprocess_dir(root, labse_model_dir=args.labse, block=args.block, min_socre=args.min,
                   clean_after_done=True, logger=logger_opus)
    else:
        for d in sub:
            preprocess_dir(os.path.join(root,d), labse_model_dir=args.labse, block=args.block, min_socre=args.min,
                       clean_after_done=True, logger=logger_opus)