# import io
# import os
# import re
# from random import random
#
# from yimt_bitext.filter.filter_score import filter_tsv_score
#
# from yimt_bitext.score.score_bitext import score_tsv
# from yimt_bitext.utils.dedup import norm
# from yimt_bitext.utils.normalizers import detok_zh_str


# def count_lines(fn):
#     print("Counting lines...")
#     lines = 0
#     interval = 500000
#     with open(fn, encoding="utf-8") as f:
#         for _ in f:
#             lines += 1
#             if lines % interval == 0:
#                 print(lines)
#
#     print(lines)
#
#     return lines


# def partition(files, n):
#     """"Partition a corpus with N sentences into a corpus with n sentences and a corpus with N-n sentences"""
#     in_files = [io.open(f, encoding="utf-8") for f in files]
#     out_files = [io.open("{}-{}".format(f, n), "w", encoding="utf-8") for f in files]
#     new_files = [io.open(f+".new", "w", encoding="utf-8") for f in files]
#
#     total = count_lines(files[0])
#     print(total)
#
#     sampled = 0
#     scanned = 0
#     sample_prob = (1.1*n) / total
#     done = False
#     for p in zip(*in_files):
#         scanned += 1
#         prob = random.uniform(0, 1)
#         if not done and prob < sample_prob:
#             for i in range(len(out_files)):
#                 out_files[i].write(p[i].strip() + "\n")
#             sampled += 1
#             if sampled % 10000 == 0:
#                 print(scanned, sampled)
#             if sampled >= n:
#                 done = True
#         else:
#             for i in range(len(new_files)):
#                 new_files[i].write(p[i].strip() + "\n")
#     print(scanned, sampled)
#
#     for f in out_files:
#         f.close()
#
#     for f in new_files:
#         f.close()


# def same_lines(path1, path2):
#     """Two text files have the same numbers of lines?"""
#     lines1 = 0
#     lines2 = 0
#     with open(path1, encoding="utf-8") as f:
#         for _ in f:
#             lines1 += 1
#
#     with open(path2, encoding="utf-8") as f:
#         for _ in f:
#             lines2 += 1
#
#     if lines1 == lines2:
#         return True
#     else:
#         return False


# def single_to_pair(src_path, tgt_path, pair_path, logger_opus=None):
#     """Combine source and target file into a parallel one"""
#     if logger_opus:
#         logger_opus.info("Merge {} {} into {}".format(src_path, tgt_path, pair_path))
#     assert same_lines(src_path, tgt_path)
#
#     cnt = 0
#     with open(src_path, encoding="utf-8") as src_f, open(tgt_path, encoding="utf-8") as tgt_f, open(pair_path, "w", encoding="utf-8") as out_f:
#         for p in zip(src_f, tgt_f):
#             out_f.write(p[0].strip() + "\t" + p[1].strip() + "\n")
#             cnt += 1
#             if cnt % 100000 == 0:
#                 if logger_opus:
#                     logger_opus.info("{}: {}".format(pair_path, cnt))
#
#         if logger_opus:
#             logger_opus.info("{}: {}".format(pair_path, cnt))


# def pair_to_single(pair_path, src_path, tgt_path):
#     """Split a parallel file into source ang target file"""
#     src_f = io.open(src_path, "w", encoding="utf-8")
#     tgt_f = io.open(tgt_path, "w", encoding="utf-8")
#
#     tsv_f = io.open(pair_path, encoding="utf-8")
#     cnt = 0
#     for line in tsv_f:
#         line = line.strip()
#         if len(line) == 0:
#             continue
#         p = line.split("\t")
#         if len(p) >= 2:
#             src_f.write(p[0] + "\n")
#             tgt_f.write(p[1] + "\n")
#
#         cnt += 1
#         if cnt % 500000 == 0:
#             print(cnt)
#
#     print(cnt)
#     src_f.close()
#     tgt_f.close()


# def merge_moses_only(in_dir, source_lang=None, target_lang=None, out_dir=None,
#                 clean_after_merge=False,logger_opus=None):
#     assert source_lang is not None or target_lang is not None
#
#     if out_dir is None:
#         out_dir = os.path.join(in_dir, "tsv")
#
#     if os.path.exists(out_dir):
#         logger_opus.info("{} exits".format(out_dir))
#         return out_dir
#
#     files = os.listdir(in_dir)
#     assert len(files)%2 == 0
#
#     files = list(sorted(files))
#
#     if not os.path.exists(out_dir):
#         os.makedirs(out_dir, exist_ok=True)
#
#     for i in range(0, len(files), 2):
#         f1 = files[i]
#         f2 = files[i+1]
#         idx = f1.rfind(".")
#         bname = f1[:idx]
#         outf = os.path.join(out_dir, bname + ".tsv")
#         f1 = os.path.join(in_dir, f1)
#         f2 = os.path.join(in_dir, f2)
#
#         if source_lang is not None:
#             if f1.endswith(source_lang):
#                 single_to_pair(f1, f2, outf, logger_opus)
#             elif f2.endswith(source_lang):
#                 single_to_pair(f2, f1, outf, logger_opus)
#         elif target_lang is not None:
#             if f1.endswith(target_lang):
#                 single_to_pair(f2, f1, outf, logger_opus)
#             elif f2.endswith(target_lang):
#                 single_to_pair(f1, f2, outf, logger_opus)
#
#         if clean_after_merge:
#             os.remove(f1)
#             os.remove(f2)
#
#     return out_dir


# def get_files(source):
#     if isinstance(source, list):
#         data_files = []
#         for f in source:
#             if os.path.isfile(f):
#                 data_files.append(f)
#             else:
#                 files = [os.path.join(f, sf) for sf in os.listdir(f)]
#                 data_files.extend(files)
#         return data_files
#     elif os.path.isdir(source):
#         data_files = [os.path.join(source, f) for f in os.listdir(source)]
#         return data_files
#     else:
#         return source


# def split(file, num_per_file=1000000, logger=None):
#     """Split corpus into multiple files with the same lines"""
#     in_file = open(file, encoding="utf-8")
#
#     cnt = 0
#     n_f = 0
#
#     if logger:
#         logger.info("Split {}: File {}".format(file, n_f))
#     out_file = open("{}-{}".format(file, n_f), "w", encoding="utf-8")
#
#     for p in in_file:
#         cnt += 1
#
#         out_file.write(p.strip() + "\n")
#
#         if cnt % 100000 == 0:
#             if logger:
#                 logger.info("Split {}: {}".format(file, cnt))
#
#         if cnt % num_per_file == 0:
#             out_file.close()
#
#             n_f += 1
#             out_file = open("{}-{}".format(file, n_f), "w", encoding="utf-8")
#             if logger:
#                 logger.info("Split {}: File {}".format(file, n_f))
#
#     out_file.close()
#
#     if logger:
#         logger.info("Split {}: {}".format(file, cnt))
from yimt_bitext.filter.filter_score import filter_tsv_score
from yimt_bitext.score.score_bitext import score_tsv


def score_and_filter_pattern(pattern, start, end, model_path, min_score=0.70, block=16, logger=None):
    for i in range(start, end):
        p = pattern.format(i)
        score_path = score_tsv(p, labse_model_dir=model_path, block=block, logger=logger)

        filter_tsv_score(score_path, min_score=min_score, logger=logger)


# def intersect(tsv_file1, tsv_file2, out_file, creterion="SRC",
#              lower=True, remove_noletter=True, logger=None):
#     if logger:
#         logger.info("Cond: {} lower: {} no_letter: {}".format(creterion, lower, remove_noletter))
#
#     pairs = set()
#     srcs = set()
#     tgts = set()
#     total = 0
#
#     if logger:
#         logger.info("Scanning {}...".format(tsv_file1))
#
#     with open(tsv_file1, encoding="utf-8") as bf:
#         for p in bf:
#             total += 1
#             if total % 100000 == 0:
#                 if logger:
#                     logger.info("{}".format(total))
#             p = p.strip()
#             pp = p.split("\t")
#             if len(pp) != 2:
#                 continue
#             src = pp[0].strip()
#             tgt = pp[1].strip()
#             src = norm(src, lower, remove_noletter)
#             hs = hash(src)
#             srcs.add(hs)
#
#             tgt = norm(tgt, lower, remove_noletter)
#             ht = hash(tgt)
#             tgts.add(ht)
#
#             p = norm(p, lower, remove_noletter)
#             h = hash(p)
#             pairs.add(h)
#
#     print(total)
#
#     intersected = 0
#     total = 0
#
#     if logger:
#         logger.info("Scanning {}...".format(tsv_file2))
#     with open(tsv_file2, encoding="utf-8") as f, open(out_file, "w", encoding="utf-8") as out_f:
#         for p in f:
#             p = p.strip()
#             total += 1
#             if total % 100000 == 0:
#                 if logger:
#                     logger.info("Total: {} Intersected: {}".format(total, intersected))
#
#             if creterion == "SRC" or creterion == "TGT":
#                 pp = p.split("\t")
#                 if len(pp) != 2:
#                     continue
#                 src = pp[0].strip()
#                 tgt = pp[1].strip()
#                 if creterion == "SRC":
#                     src = norm(src, lower, remove_noletter)
#                     hs = hash(src)
#                     if hs in srcs:
#                         out_f.write(p + "\n")
#                         intersected += 1
#                 else:
#                     tgt = norm(tgt, lower, remove_noletter)
#                     ht = hash(tgt)
#                     if ht in tgts:
#                         out_f.write(p + "\n")
#                         intersected += 1
#             else:
#                 pn = norm(p, lower, remove_noletter)
#                 h = hash(pn)
#                 if h in pairs:
#                     out_f.write(p + "\n")
#                     intersected += 1
#
#     if logger:
#         logger.info("Total: {} Intersected: {}".format(total, intersected))


# def detok_zh_file(in_file, out_file=None):
#     if out_file is None:
#         out_file = in_file + ".detok"
#
#     outf = open(out_file, "w", encoding="utf-8")
#
#     with open(in_file, encoding="utf-8") as inf:
#         for line in inf:
#             line = line.strip()
#             line = re.sub(r"\s{2,}", " ", line)
#             line = line.strip()
#             line = detok_zh_str(line)
#             outf.write(line + "\n")
#
#     outf.close()


# def diff(tsv_file1, tsv_file2, out_file=None, creterion="SRC",
#              lower=True, remove_noletter=True,
#          logger=None):
#     if logger:
#         logger.info("Cond: {} lower: {} no_letter: {}".format(creterion, lower, remove_noletter))
#
#     if out_file is None:
#         out_file = tsv_file1 + ".diffed"
#     pairs = set()
#     srcs = set()
#     tgts = set()
#     total = 0
#
#     if logger:
#         logger.info("Scanning file2...")
#
#     with open(tsv_file2, encoding="utf-8") as bf:
#         for p in bf:
#             total += 1
#             if total % 10000 == 0:
#                 if logger:
#                     logger.info("{}: {}".format(tsv_file2, total))
#             p = p.strip()
#             pp = p.split("\t")
#             if len(pp) != 2:
#                 continue
#             src = pp[0].strip()
#             tgt = pp[1].strip()
#             src = norm(src, lower, remove_noletter)
#             hs = hash(src)
#             srcs.add(hs)
#
#             tgt = norm(tgt, lower, remove_noletter)
#             ht = hash(tgt)
#             tgts.add(ht)
#
#             p = norm(p, lower, remove_noletter)
#             h = hash(p)
#             pairs.add(h)
#
#     if logger:
#         logger.info("{}: {}".format(tsv_file2, total))
#
#     differed = 0
#     total = 0
#
#     if logger:
#         logger.info("Scanning file1...")
#
#     with open(tsv_file1, encoding="utf-8") as f, open(out_file, "w", encoding="utf-8") as out_f:
#         for p in f:
#             p = p.strip()
#             total += 1
#             if total % 100000 == 0:
#                 if logger:
#                     logger.info("Total: {}, Difference: {}".format(total, differed))
#
#             if creterion == "SRC" or creterion == "TGT":
#                 pp = p.split("\t")
#                 if len(pp) != 2:
#                     continue
#                 src = pp[0].strip()
#                 tgt = pp[1].strip()
#                 if creterion == "SRC":
#                     src = norm(src, lower, remove_noletter)
#                     hs = hash(src)
#                     if hs not in srcs:
#                         out_f.write(p + "\n")
#                         differed += 1
#                 else:
#                     tgt = norm(tgt, lower, remove_noletter)
#                     ht = hash(tgt)
#                     if ht not in tgts:
#                         out_f.write(p + "\n")
#                         differed += 1
#             else:
#                 pn = norm(p, lower, remove_noletter)
#                 h = hash(pn)
#                 if h not in pairs:
#                     out_f.write(p + "\n")
#                     differed += 1
#
#     if logger:
#         logger.info("Total: {}, Difference: {}".format(total, differed))
