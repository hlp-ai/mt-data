"""将X-EN语料通过EN-ZH翻译转换成X-ZH平行语料"""
import os
import re
import shutil
import time
from argparse import ArgumentParser

import ctranslate2

from yimt_bitext.split.merge import merge_files
from yimt_bitext.split.sp import tokenize_file, detokenize_file, load_spm
from yimt_bitext.split.split_file import split
from yimt_bitext.split.to_pair import single_to_pair
from yimt_bitext.split.to_single import pair_to_single
from yimt_bitext.split.tokenization import detok_zh_file
from yimt_bitext.utils.log import get_logger


def _translate(translator, in_file, out_file, batch_size=32, logger=None):
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
            max_batch_size=batch_size*20,
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


def aug_pivot(tsv_file, sp_en, sp_zh, translator, src_lang, tgt_lang="en", clean_after_done=False,
              batch_size=32, logger=None):
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
    if clean_after_done:
        os.remove(to_translate)

    out_file = tok_output + ".tozh"
    if logger:
        logger.info("Translating {} into {}...".format(tok_output, out_file))
    _translate(translator, tok_output, out_file, batch_size=batch_size, logger=logger)
    if clean_after_done:
        os.remove(tok_output)

    detok_file = out_file + ".det"

    if logger:
        logger.info("Detokenizing {} into {}...".format(out_file, detok_file))
    detokenize_file(sp_zh, out_file, detok_file)
    if clean_after_done:
        os.remove(out_file)

    zh_file = detok_file + ".zh"
    detok_zh_file(detok_file, zh_file)
    if clean_after_done:
        os.remove(detok_file)

    single_to_pair(un_translate, zh_file, tsv_file + ".aug2zh", logger_opus=logger)
    if clean_after_done:
        os.remove(un_translate)
        os.remove(zh_file)


def aug_from_en(path, sp_en_file, sp_zh_file, ct2_zh_model, src_lang,
                clean_after_done=True, batch_size=32,
                logger=None):
    logger.info("***Translating***")

    logger.info("Splitting")
    split_dir = os.path.join(os.path.dirname(path), "aug")
    if not os.path.exists(split_dir):
        os.mkdir(split_dir)
        path = shutil.move(path, split_dir)
        split(path, logger=logger)
    else:
        logger.info("{} exits".format(split_dir))

    logger.info("Loading SP model...")

    sp_en = load_spm(sp_en_file)
    sp_zh = load_spm(sp_zh_file)

    logger.info("Loading ctranslate2 model...")

    translator = ctranslate2.Translator(ct2_zh_model, device="cuda")

    files = os.listdir(split_dir)
    for f in files:
        if re.match(r".+\d+$", f):
            tsv_file = os.path.join(split_dir, f)
            out_path = tsv_file + ".aug2zh"
            if os.path.exists(out_path):
                logger.info("{} exists".format(out_path))
                continue

            logger.info("Translating file...")
            aug_pivot(tsv_file, sp_en, sp_zh, translator, src_lang,
                      clean_after_done=clean_after_done, batch_size=batch_size,
                      logger=logger)

    logger.info("Merging augmented files...")
    files = os.listdir(split_dir)
    to_merge = []
    for f in files:
        f = os.path.join(split_dir, f)
        if f.endswith(".aug2zh"):
            to_merge.append(f)
    out_file = os.path.join(os.path.join(split_dir, os.path.basename(path) + ".2zh"))
    merge_files(to_merge, out_file, logger_opus=logger)

    return out_file


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--input", required=True, help="input file")
    argparser.add_argument("-se", "--sp_en_model",
                           default=r"D:\kidden\mt\mt-exp\sp\opus-enzh-all-sf.en-sp-32000.model",
                           help="EN sp model path")
    argparser.add_argument("-sz", "--sp_zh_model",
                           default=r"D:\kidden\mt\mt-exp\sp\opus-enzh-all-sf.zh.pretok-sp-32000.model",
                           help="ZH sp model path")
    argparser.add_argument("-m", "--ct2_zh_model",
                           default=r"D:\kidden\mt\mt-exp\en-zh\opus\ct2",
                           help="en-to-zh ct2 model path")
    argparser.add_argument("--src_lang", required=True, help="source language")
    argparser.add_argument("--bs", type=int, default=32, help="batch size")
    argparser.add_argument("--clean", action="store_true", help="clean after processing")
    argparser.add_argument("--log_dir", default="./", help="log directory")
    args = argparser.parse_args()

    logger = get_logger(os.path.join(args.log_dir, "opus.log"), "Pipeline")

    aug_from_en(args.input, args.sp_en_model, args.sp_zh_model, args.ct2_zh_model, args.src_lang, args.clean,
                args.bs, logger)
