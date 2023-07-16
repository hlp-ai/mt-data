import io
import os
import re
import time
import zipfile

from yimt_bitext.opus.bitext_scorers import LaBSEScorer
from yimt_bitext.utils.dedup import norm
from yimt_bitext.utils.normalizers import detok_zh_file_inplace, detok_zh_str


def extract_zips(zips_dir, out_dir=None, logger_opus=None):
    """Unzip zip files in a directory into out directory"""
    if out_dir is None:
        out_dir = os.path.join(zips_dir, "unzip")

    if os.path.exists(out_dir):
        logger_opus.info("{} exits".format(out_dir))
        return out_dir

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


def pair_to_single(pair_path, src_path, tgt_path):
    """Split a parallel file into source ang target file"""
    src_f = io.open(src_path, "w", encoding="utf-8")
    tgt_f = io.open(tgt_path, "w", encoding="utf-8")

    tsv_f = io.open(pair_path, encoding="utf-8")
    cnt = 0
    for line in tsv_f:
        line = line.strip()
        if len(line) == 0:
            continue
        p = line.split("\t")
        if len(p) >= 2:
            src_f.write(p[0] + "\n")
            tgt_f.write(p[1] + "\n")

        cnt += 1
        if cnt % 500000 == 0:
            print(cnt)

    print(cnt)
    src_f.close()
    tgt_f.close()


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

        if clean_after_merge:
            os.remove(f1)
            os.remove(f2)

    return out_dir


def get_files(source):
    if isinstance(source, list):
        data_files = []
        for f in source:
            if os.path.isfile(f):
                data_files.append(f)
            else:
                files = [os.path.join(f, sf) for sf in os.listdir(f)]
                data_files.extend(files)
        return data_files
    elif os.path.isdir(source):
        data_files = [os.path.join(source, f) for f in os.listdir(source)]
        return data_files
    else:
        return source


def merge(source, out_fn, clean_after_merge=False, max=-1, logger_opus=None):
    data_files = get_files(source)

    out_path = out_fn
    if os.path.exists(out_path):
        logger_opus.info("{} exits".format(out_path))
        return out_path

    out_path = merge_files(data_files, out_path, clean_after_merge=clean_after_merge, max=max, logger_opus=logger_opus)

    return out_path


def merge_files(data_files, out_path, clean_after_merge=False, max=-1, logger_opus=None):
    """Merge files into one file"""
    total = 0
    with open(out_path, "w", encoding="utf-8") as out_f:
        for f in data_files:
            cnt = 0
            with open(f, encoding="utf-8") as in_f:
                for line in in_f:
                    line = line.strip()
                    if len(line) > 0:
                        out_f.write(line + "\n")
                        total += 1
                        cnt += 1
                        if total % 100000 == 0:
                            if logger_opus:
                                logger_opus.info("Merging {} into {}: {}/{}".format(f, out_path, cnt, total))
                        if 0 < max <= total:
                            if logger_opus:
                                logger_opus.info("Merged {}, reach max".format(total))
                            break

            if logger_opus:
                logger_opus.info("Merged {} into {}: {}/{}".format(f, out_path, cnt, total))

        if logger_opus:
            logger_opus.info("Merged {}: {}".format(out_path, total))

    if clean_after_merge:
        for f in data_files:
            os.remove(f)

    return out_path


def split(file, num_per_file=500000, logger=None):
    """Split corpus into multiple files with the same lines"""
    in_file = open(file, encoding="utf-8")

    cnt = 0
    n_f = 0

    if logger:
        logger.info("Split {}: File {}".format(file, n_f))
    out_file = open("{}-{}".format(file, n_f), "w", encoding="utf-8")

    for p in in_file:
        cnt += 1

        out_file.write(p.strip() + "\n")

        if cnt % 100000 == 0:
            if logger:
                logger.info("Split {}: {}".format(file, cnt))

        if cnt % num_per_file == 0:
            out_file.close()

            n_f += 1
            out_file = open("{}-{}".format(file, n_f), "w", encoding="utf-8")
            if logger:
                logger.info("Split {}: File {}".format(file, n_f))

    out_file.close()

    if logger:
        logger.info("Split {}: {}".format(file, cnt))


def score_tsv(in_path, out_path=None,
         labse_model_dir="D:/kidden/mt/open/mt-ex/mt/data/labse1",
         block=8, max_seq_len=48,
              clean_after_done=False, logger=None
         ):
    scorer = LaBSEScorer(labse_model_dir, max_seq_len)

    lines = open(in_path, encoding="utf-8").readlines()
    if logger:
        logger.info("# of lines: {}".format(len(lines)))

    if out_path is None:
        out_path = in_path + ".score"

    if os.path.exists(out_path):
        logger.info("{} exists".format(out_path))
        return out_path

    out_f = open(out_path, "w", encoding="utf-8")

    n = 0
    start = time.time()
    for i in range(0, len(lines), block):
        buf = lines[i:i+block]
        srcs = []
        tgts = []
        for line in buf:
            line = line.strip()
            pair = line.split("\t")
            src = pair[0]
            tgt = pair[1]
            srcs.append(src)
            tgts.append(tgt)

        ss = scorer.score(srcs, tgts)
        for j in range(len(ss)):
            out_f.write("{:.4f}\t{}\t{}\n".format(ss[j], srcs[j], tgts[j]))

        n += len(buf)
        if n % (40*block) == 0:
            t = time.time() - start
            if logger:
                logger.info("{}: {:.2f} pairs/sec".format(n, n/t))

    out_f.close()

    if clean_after_done:
        os.remove(in_path)

    return out_path


def diff_tsv(tsv_file1, tsv_file2, out_file=None, creterion="SRC",
             lower=True, remove_noletter=True,
             logger=None):
    if out_file is None:
        out_file = tsv_file1 + ".diff"
    pairs = set()
    srcs = set()
    tgts = set()
    total = 0

    if logger:
        logger.info("Scanning {}...".format(tsv_file2))
    with open(tsv_file2, encoding="utf-8") as bf:
        for p in bf:
            total += 1
            if total % 100000 == 0:
                if logger:
                    logger.info("{}".format(total))
            p = p.strip()
            pp = p.split("\t")
            if len(pp) != 2:
                continue
            src = pp[0].strip()
            tgt = pp[1].strip()
            src = norm(src, lower, remove_noletter)
            hs = hash(src)
            srcs.add(hs)

            tgt = norm(tgt, lower, remove_noletter)
            ht = hash(tgt)
            tgts.add(ht)

            p = norm(p, lower, remove_noletter)
            h = hash(p)
            pairs.add(h)

    if logger:
        logger.info("{}".format(total))

    differed = 0
    total = 0

    if logger:
        logger.info("Scanning {}...".format(tsv_file1))
    with open(tsv_file1, encoding="utf-8") as f, open(out_file, "w", encoding="utf-8") as out_f:
        for p in f:
            p = p.strip()
            total += 1
            if total % 100000 == 0:
                if logger:
                    logger.info("Total: {}, Diff: {}".format(total, differed))

            if creterion == "SRC" or creterion == "TGT":
                pp = p.split("\t")
                if len(pp) != 2:
                    continue
                src = pp[0].strip()
                tgt = pp[1].strip()
                if creterion == "SRC":
                    src = norm(src, lower, remove_noletter)
                    hs = hash(src)
                    if hs not in srcs:
                        out_f.write(p + "\n")
                        differed += 1
                else:
                    tgt = norm(tgt, lower, remove_noletter)
                    ht = hash(tgt)
                    if ht not in tgts:
                        out_f.write(p + "\n")
                        differed += 1
            else:
                pn = norm(p, lower, remove_noletter)
                h = hash(pn)
                if h not in pairs:
                    out_f.write(p + "\n")
                    differed += 1

    if logger:
        logger.info("Total: {}, Diff: {}".format(total, differed))


def filter_tsv(in_path, out_path, min_score, logger=None):
    total = 0
    left = 0
    with open(in_path, encoding="utf-8") as in_f, open(out_path, "w", encoding="utf-8") as out_f:
        for line in in_f:
            total += 1
            if total % 100000 == 0:
                if logger:
                    logger.info("Total: {}, Left: {}".format(total, left))
            line = line.strip()
            parts = line.split("\t")
            if len(parts) != 3:
                continue

            if float(parts[0]) > min_score:
                out_f.write(parts[1] + "\t" + parts[2] + "\n")
                left += 1

    if logger:
        logger.info("Total: {}, Left: {}".format(total, left))


def detok_zh_file(in_file, out_file=None):
    if out_file is None:
        out_file = in_file + ".detok"

    outf = open(out_file, "w", encoding="utf-8")

    with open(in_file, encoding="utf-8") as inf:
        for line in inf:
            line = line.strip()
            line = re.sub(r"\s{2,}", " ", line)
            line = line.strip()
            line = detok_zh_str(line)
            outf.write(line + "\n")

    outf.close()