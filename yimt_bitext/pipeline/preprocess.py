"""对OPUS语料进行预处理：解压、合并、规范化、去重、过滤、打分过滤"""
import os
import re
import shutil
from argparse import ArgumentParser
from pathlib import Path

from yimt_bitext.dedup.dedup import dedup_tsv_file
from yimt_bitext.filter.filters import EmptyFilter, SameFilter, OverlapFilter, AlphabetRatioFilter, \
    RepetitionFilter, LengthFilter, CharacterRatioFilter
from yimt_bitext.filter.filter import filter_file
from yimt_bitext.normalize.normalizers import ToZhNormalizer, CleanerTSV, DeTokenizer
from yimt_bitext.normalize.normalize import normalize_file
from yimt_bitext.score.score_bitext import score_tsv
from yimt_bitext.filter.filter_score import filter_tsv_score
from yimt_bitext.opus.merge_moses import merge_moses
from yimt_bitext.opus.unzip_files import extract_zips
from yimt_bitext.split.merge import merge
from yimt_bitext.split.split_file import split
from yimt_bitext.utils.chars import get_lang2script
from yimt_bitext.utils.log import get_logger

lang2script = get_lang2script()


def preprocess_dir(in_dir,
                   labse_model_dir="D:/kidden/mt/open/mt-ex/mt/data/labse1",
                   block=8,
                   min_score=0.6,
                   clean_after_done=False,
                   max=-1,
                   logger=None):
    logger.info("Preprocessing {}".format(in_dir))

    parts = Path(in_dir).parts
    dirname = parts[-1]
    langs = dirname.split("-")
    if len(langs) == 2:
        sl, tl = langs
        target_lang = tl
    else:
        logger.warn("No language pair exist: {}".format(dirname))
        return in_dir

    logger.info(dirname)

    logger.info("***Unzipping***")
    path = extract_zips(in_dir, logger_opus=logger)

    logger.info("***Merging Moses***")
    path = merge_moses(path, target_lang=target_lang, clean_after_merge=clean_after_done, logger_opus=logger)

    logger.info("***Merging Files***")
    path = merge(path, os.path.join(path, dirname + ".tsv"), clean_after_merge=clean_after_done, max=max,
                 logger_opus=logger)

    logger.info("***Normalizing***")
    if target_lang == "zh":
        normalizers = [ToZhNormalizer(), DeTokenizer()]
    else:
        normalizers = [CleanerTSV()]

    logger.info(normalizers)
    path = normalize_file(path, normalizers, clean_after_done=clean_after_done, logger=logger)

    logger.info("***Deduping***")
    path = dedup_tsv_file(path, dedup_srctgt=False, dedup_src=True, dedup_tgt=False,
                          remove_noletter=False, clean_after_done=clean_after_done, logger=logger)

    logger.info("***Filtering***")
    filters = [EmptyFilter(), SameFilter(), OverlapFilter(ratio=0.80),
               AlphabetRatioFilter(threshold=0.33, exclude_whitespace=True), RepetitionFilter()]
    langs = dirname.split("-")
    if len(langs) == 2:
        sl, tl = langs
        src_script = lang2script[sl]
        tgt_script = lang2script[tl]
        char_filter = CharacterRatioFilter(scripts=(src_script, tgt_script), thresholds=(0.60, 0.60))
        filters.append(char_filter)

        if target_lang == "en":
            tgt_len = LengthFilter.space_sep_len_f
            filters.append(LengthFilter(tgt_len_fn=tgt_len, tgt_lens=(1, 128)))

    logger.info(filters)

    path = filter_file(path, filters=filters, clean_after_done=clean_after_done, logger=logger)

    logger.info("***Splitting***")
    split_dir = os.path.join(os.path.dirname(path), "score")
    if not os.path.exists(split_dir):
        os.mkdir(split_dir)
        path = shutil.move(path, split_dir)
        split(path, logger=logger)
    else:
        logger_opus.info("{} exits".format(split_dir))

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
    else:
        logger.info("{} exists".format(filter_dir))
    files = os.listdir(split_dir)
    for f in files:
        if f.endswith(".score"):
            logger.info("Filter {} by score".format(f))
            out_path = os.path.join(filter_dir, f + ".sfilter")
            if os.path.exists(out_path):
                logger.info("{} exists".format(out_path))
                continue
            filter_tsv_score(os.path.join(split_dir, f), out_path, min_score, logger=logger)

    logger.info("***Merging Files***")
    out_path = os.path.join(filter_dir, dirname + "-preprocessed.tsv")
    if not os.path.exists(out_path):
        path = merge(filter_dir, out_path, clean_after_merge=clean_after_done, logger_opus=logger)
    else:
        logger.info("{} exists".format(out_path))

    return path


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--root", required=True, help="Root dir")
    argparser.add_argument("--labse", default="D:/kidden/mt/open/mt-ex/mt/data/labse1", help="directory for labse")
    argparser.add_argument("--block", type=int, default=8, help="block size for labse")
    argparser.add_argument("--min", type=float, default=0.6, help="min socre for filtering")
    argparser.add_argument("--clean", action="store_true", help="clean after processing")
    argparser.add_argument("--max_pairs", default=-1, type=int, help="max number of pairs for each corpus")
    argparser.add_argument("--log_dir", default="./", help="log directory")
    args = argparser.parse_args()

    logger_opus = get_logger(os.path.join(args.log_dir, "opus.log"), "Pipeline")

    root = args.root
    sub = os.listdir(root)
    contain_langs = all([os.path.isdir(os.path.join(root, d)) for d in sub])
    if not contain_langs:
        preprocess_dir(root, labse_model_dir=args.labse, block=args.block, min_score=args.min,
                       clean_after_done=args.clean, max=args.max_pairs, logger=logger_opus)
    else:
        for d in sub:
            preprocess_dir(os.path.join(root, d), labse_model_dir=args.labse, block=args.block, min_score=args.min,
                           clean_after_done=args.clean, max=args.max_pairs, logger=logger_opus)
