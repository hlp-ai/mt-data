import os
import sys
import zipfile

from yimt_bitext.utils.clean import clean_file
from yimt_bitext.utils.dedup import dedup_file
from yimt_bitext.utils.log import get_logger
from yimt_bitext.utils.normalizers import detok_zh_file_inplace, normalize_file, ToZhNormalizer


def extract_zips(zips_dir, out_dir=None, logger_opus=None):
    """Unzip zip files in a directory into out directory"""
    if out_dir is None:
        out_dir = os.path.join(zips_dir, "unzip")

    zips = os.listdir(zips_dir)
    for zipf in zips:
        if not zipf.endswith(".zip"):
            continue

        if logger_opus:
            logger_opus.info("Unzip {}".format(zipf))

        zFile = zipfile.ZipFile(os.path.join(zips_dir, zipf), "r")
        for fileM in zFile.namelist():
            if fileM.rfind(".") == len(fileM)-3 or fileM.rfind(".") == len(fileM)-6:
                zFile.extract(fileM, out_dir)
        zFile.close()

    return out_dir


def same_lines(path1, path2):
    """Two text files have the same numbers of lines?"""
    lines1 = 0
    lines2 = 0
    with open(path1, encoding="utf-8") as f:
        for _ in f:
            lines1 += 1

    with open(path2, encoding="utf-8") as f:
        for _ in f:
            lines2 += 1

    if lines1 == lines2:
        return True
    else:
        return False


def single_to_pair(src_path, tgt_path, pair_path, logger_opus=None):
    """Combine source and target file into a parallel one"""
    logger_opus.info("Merge {} {} into {}".format(src_path, tgt_path, pair_path))
    assert same_lines(src_path, tgt_path)

    cnt = 0
    with open(src_path, encoding="utf-8") as src_f, open(tgt_path, encoding="utf-8") as tgt_f, open(pair_path, "w", encoding="utf-8") as out_f:
        for p in zip(src_f, tgt_f):
            out_f.write(p[0].strip() + "\t" + p[1].strip() + "\n")
            cnt += 1
            if cnt % 100000 == 0:
                if logger_opus:
                    logger_opus.info("{}: {}".format(pair_path, cnt))

        if logger_opus:
            logger_opus.info("{}: {}".format(pair_path, cnt))


def merge_moses(in_dir, source_lang=None, target_lang=None, out_dir=None, logger_opus=None):
    assert source_lang is not None or target_lang is not None

    if out_dir is None:
        out_dir = os.path.join(in_dir, "tsv")

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

        if f1.endswith("zh") and (f1.find("bible") >= 0 or f1.find("XLEnt") >= 0):
            logger_opus.info("Detokenizing {}".format(f1))
            detok_zh_file_inplace(f1)
        elif f2.endswith("zh") and (f2.find("bible") >= 0 or f2.find("XLEnt") >= 0):
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

    return out_dir


def merge_files(data_root, out_fn, logger_opus=None):
    """Merge files in a directory into one file"""
    data_files = [os.path.join(data_root, f) for f in os.listdir(data_root)]

    out_path = os.path.join(data_root, out_fn)

    cnt = 0
    with open(out_path, "w", encoding="utf-8") as out_f:
        for f in data_files:
            in_f = open(f, encoding="utf-8")
            for line in in_f:
                line = line.strip()
                if len(line) > 0:
                    out_f.write(line + "\n")
                    cnt += 1
                    if cnt % 100000 == 0:
                        if logger_opus:
                            logger_opus.info("Merging {}: {}".format(out_path, cnt))

        if logger_opus:
            logger_opus.info("Merging {}: {}".format(out_path, cnt))

    return out_path
