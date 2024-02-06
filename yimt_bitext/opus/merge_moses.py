"""合并给定目录下各个语料的单语文件为平行语料TSV文件"""
import argparse
import os

from yimt_bitext.split.to_pair import single_to_pair
from yimt_bitext.utils.log import get_logger
from yimt_bitext.normalize.normalizers import detok_zh_file_inplace


def merge_moses(in_dir, source_lang=None, target_lang=None, out_dir=None,
                clean_after_merge=False,logger_opus=None):
    assert source_lang is not None or target_lang is not None

    if out_dir is None:
        out_dir = os.path.join(in_dir, "tsv")

    if os.path.exists(out_dir):
        logger_opus.info("{} exits".format(out_dir))
        return out_dir

    files = os.listdir(in_dir)
    assert len(files)%2 == 0

    files = list(sorted(files))

    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    for i in range(0, len(files), 2):
        f1 = files[i]
        f2 = files[i+1]
        idx = f1.rfind(".")
        bname = f1[:idx]
        outf = os.path.join(out_dir, bname + ".tsv")
        f1 = os.path.join(in_dir, f1)
        f2 = os.path.join(in_dir, f2)

        if f1.endswith("zh") and (f1.find("bible") >= 0 or f1.find("XLEnt") >= 0 or f1.find("SPC") >= 0) :
            logger_opus.info("Detokenizing {}".format(f1))
            detok_zh_file_inplace(f1)
        elif f2.endswith("zh") and (f2.find("bible") >= 0 or f2.find("XLEnt") >= 0 or f2.find("SPC") >= 0):
            logger_opus.info("Detokenizing {}".format(f2))
            detok_zh_file_inplace(f2)

        if source_lang is not None:
            if f1.endswith(source_lang):
                single_to_pair(f1, f2, outf, logger_opus)
            elif f2.endswith(source_lang):
                single_to_pair(f2, f1, outf, logger_opus)
        elif target_lang is not None:
            if f1.endswith(target_lang):
                single_to_pair(f2, f1, outf, logger_opus)
            elif f2.endswith(target_lang):
                single_to_pair(f1, f2, outf, logger_opus)

        if clean_after_merge:
            os.remove(f1)
            os.remove(f2)

    return out_dir


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--input", type=str, required=True, help="input dir")
    argparser.add_argument("-o", "--output", type=str, default=None, help="output dir")
    argparser.add_argument("-sl", "--src_lang", type=str, default=None, help="source language")
    argparser.add_argument("-tl", "--tgt_lang", type=str, default=None, help="target language")
    args = argparser.parse_args()

    logger = get_logger("./log.txt", "OPUS")

    merge_moses(args.input, args.src_lang, args.tgt_lang, args.output, logger_opus=logger)
