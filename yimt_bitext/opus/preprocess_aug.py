import os
import re
import shutil
import time
from argparse import ArgumentParser
from pathlib import Path

import ctranslate2

from yimt_bitext.opus.utils import extract_zips, merge_moses, split, score_tsv, merge, filter_tsv, pair_to_single, \
    single_to_pair, detok_zh_file
from yimt_bitext.utils.dedup import dedup_bitext_file
from yimt_bitext.utils.filters import filter_file, EmptyFilter, SameFilter, OverlapFilter, NonZeroNumeralsFilter, \
    AlphabetRatioFilter, RepetitionFilter, CharacterRatioFilter, get_lang2script
from yimt_bitext.utils.log import get_logger
from yimt_bitext.utils.normalizers import ToZhNormalizer, normalize_file, CleanerTSV
from yimt_bitext.utils.sp import tokenize_file, detokenize_file, load_spm

lang2script = get_lang2script()


def preprocess_dir(in_dir, sp_en, sp_zh, translator,
                   target_lang="zh",
               labse_model_dir="D:/kidden/mt/open/mt-ex/mt/data/labse1",
               block=8,
               min_socre=0.6,
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

    logger.info("***Unzipping***")
    path = extract_zips(in_dir, logger_opus=logger)

    logger.info("***Merging Moses***")
    path = merge_moses(path, target_lang=target_lang, clean_after_merge=clean_after_done, logger_opus=logger)

    logger.info("***Merging Files***")
    path = merge(path, os.path.join(path, dirname + ".tsv"), clean_after_merge=clean_after_done, max=max, logger_opus=logger)

    logger.info("***Normalizing***")
    if target_lang == "zh":
        normalizers = [ToZhNormalizer()]
    else:
        normalizers = [CleanerTSV()]
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
            out_path = os.path.join(filter_dir, f+".sfilter")
            if os.path.exists(out_path):
                logger.info("{} exists".format(out_path))
                logger.info("**Translating file***")
                aug_pivot(out_path, sp_en, sp_zh, translator, sl, tgt_lang=tl, logger=logger)
                continue
            filter_tsv(os.path.join(split_dir, f), out_path, min_socre, logger=logger)

            logger.info("**Translating file***")
            aug_pivot(out_path, sp_en, sp_zh, translator, sl, tgt_lang=tl, logger=logger)

    return path


def _translate(translator, in_file, out_file, batch_size = 48, logger=None):
    with open(in_file, encoding="utf-8") as f:
        lines = f.readlines()

    out = open(out_file, "w", encoding="utf-8")

    start = time.time()
    n = 0
    for i in range(0, len(lines), batch_size):
        if i + batch_size < len(lines):
            to_translate = lines[i:i + batch_size]
        else:
            to_translate = lines[i:]

        to_translate = [s.strip().split() for s in to_translate]

        translations_tok = translator.translate_batch(
            source=to_translate,
            beam_size=5,
            batch_type="tokens",
            max_batch_size=1024,
            replace_unknowns=True,
            repetition_penalty=1.2,
            target_prefix=None,
        )

        translations = [" ".join(translation[0]["tokens"])
                        for translation in translations_tok]

        n += len(to_translate)

        if n%(batch_size*10) == 0:
            etime = time.time() - start
            speed = float(n) / etime
            if logger:
                logger.info("{} sentences, {:.2f} sentences/sec, {:.2f} sec".format(n, speed, etime))

        for t in translations:
            out.write(t + "\n")

    out.close()

    etime = time.time() - start
    speed = float(n) / etime
    if logger:
        logger.info("{} sentences, {:.2f} sentences/sec, {:.2f} sec".format(n, speed, etime))


def aug_pivot(tsv_file, sp_en, sp_zh, translator, src_lang, tgt_lang="en", logger=None):
    if logger:
        logger.info("Processing {}".format(tsv_file))
    src_file = tsv_file + "." + src_lang
    tgt_file = tsv_file + "." + tgt_lang

    if src_lang == "en":
        to_translate = src_file
        un_translate = tgt_file
    else:
        to_translate = tgt_file
        un_translate = src_file

    if logger:
        logger.info("Splitting {} into {} and {}...".format(tsv_file, src_file, tgt_file))
    pair_to_single(tsv_file, src_file, tgt_file)

    tok_output = to_translate + ".tok"
    if logger:
        logger.info("Tokenizing {} into {}...".format(to_translate, tok_output))
    tokenize_file(sp_en, to_translate, tok_output)

    out_file = tok_output + ".tozh"
    if logger:
        logger.info("Translating {} into {}...".format(tok_output, out_file))
    _translate(translator, tok_output, out_file)

    detok_file = out_file + ".det"

    if logger:
        logger.info("Detokenizing {} into {}...".format(out_file, detok_file))
    detokenize_file(sp_zh, out_file, detok_file)

    zh_file = detok_file + ".zh"
    detok_zh_file(detok_file, zh_file)

    single_to_pair(un_translate, zh_file, tsv_file + ".aug2zh")


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--root", required=True, help="Root dir")
    argparser.add_argument("--tl", default="zh", help="target language")
    argparser.add_argument("--labse", default="D:/kidden/mt/open/mt-ex/mt/data/labse1", help="directory for labse")
    argparser.add_argument("--block", type=int, default=8, help="block size for labse")
    argparser.add_argument("--min", type=float, default=0.6, help="min socre for filtering")
    argparser.add_argument("--clean", action="store_true", help="min socre for filtering")
    argparser.add_argument("--max_pairs", default=-1, type=int, help="max number of pairs for each corpus")
    argparser.add_argument("-se", "--sp_en_model",
                           default=r"D:\kidden\mt\mt-exp\sp\opus-enzh-all-sf.en-sp-32000.model",
                           help="EN sp model path")
    argparser.add_argument("-sz", "--sp_zh_model",
                           default=r"D:\kidden\mt\mt-exp\sp\opus-enzh-all-sf.zh.pretok-sp-32000.model",
                           help="ZH sp model path")
    argparser.add_argument("-m", "--ct2_zh_model",
                           default=r"D:\kidden\mt\mt-exp\en-zh\opus\ct2",
                           help="en-to-zh ct2 model path")
    argparser.add_argument("--log_dir", default="./", help="log directory")
    args = argparser.parse_args()

    logger_opus = get_logger(os.path.join(args.log_dir, "opus.log"), "OPUS")

    logger_opus.info("Loading SP model...")

    sp_en_file = args.sp_en_model  # r"/home/liuxf/hdisk/exp/sp/opus-enzh-all-sf.en-sp-32000.model"
    sp_en = load_spm(sp_en_file)

    sp_zh_file = args.sp_zh_model  # r"/home/liuxf/hdisk/exp/sp/opus-enzh-all-sf.zh.pretok-sp-32000.model"
    sp_zh = load_spm(sp_zh_file)

    logger_opus.info("Loading ctranslate2 model...")

    translator = ctranslate2.Translator(
        args.ct2_zh_model,
        device="cuda"
    )

    root = args.root
    sub = os.listdir(root)
    contain_langs = all([os.path.isdir(os.path.join(root,d)) for d in sub])
    if not contain_langs:
        preprocess_dir(root, sp_en, sp_zh, translator, labse_model_dir=args.labse, block=args.block, min_socre=args.min,
                   clean_after_done=args.clean, max=args.max_pairs, logger=logger_opus)
    else:
        for d in sub:
            preprocess_dir(os.path.join(root,d), sp_en, sp_zh, translator, labse_model_dir=args.labse, block=args.block, min_socre=args.min,
                       clean_after_done=args.clean, max=args.max_pairs, logger=logger_opus)