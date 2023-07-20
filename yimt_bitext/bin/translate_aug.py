import os
import re
import shutil
from argparse import ArgumentParser

import ctranslate2

from yimt_bitext.opus.preprocess_aug import aug_pivot
from yimt_bitext.opus.utils import split
from yimt_bitext.utils.log import get_logger
from yimt_bitext.utils.sp import load_spm


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
    argparser.add_argument("--log_dir", default="./", help="log directory")
    args = argparser.parse_args()

    logger = get_logger(os.path.join(args.log_dir, "opus.log"), "OPUS")

    logger.info("***Splitting***")
    path = args.input
    split_dir = os.path.join(os.path.dirname(path), "aug")
    if not os.path.exists(split_dir):
        os.mkdir(split_dir)
        path = shutil.move(path, split_dir)
        split(path, logger=logger)
    else:
        logger.info("{} exits".format(split_dir))

    logger.info("Loading SP model...")

    sp_en_file = args.sp_en_model  # r"/home/liuxf/hdisk/exp/sp/opus-enzh-all-sf.en-sp-32000.model"
    sp_en = load_spm(sp_en_file)

    sp_zh_file = args.sp_zh_model  # r"/home/liuxf/hdisk/exp/sp/opus-enzh-all-sf.zh.pretok-sp-32000.model"
    sp_zh = load_spm(sp_zh_file)

    logger.info("Loading ctranslate2 model...")

    translator = ctranslate2.Translator(
        args.ct2_zh_model,
        device="cuda"
    )

    files = os.listdir(split_dir)
    for f in files:
        if re.match(r".+\d+$", f):
            tsv_file = os.path.join(split_dir, f)
            out_path = tsv_file + ".aug2zh"
            if os.path.exists(out_path):
                logger.info("{} exists".format(out_path))
                continue

            logger.info("**Translating file***")
            aug_pivot(out_path, sp_en, sp_zh, translator, args.src_lang, logger=logger)
