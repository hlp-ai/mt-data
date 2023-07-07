import os
import re
import shutil
from argparse import ArgumentParser

from yimt_bitext.opus.utils import split, score_tsv, merge, filter_tsv
from yimt_bitext.utils.log import get_logger


def score_and_filter(path,
               labse_model_dir="D:/kidden/mt/open/mt-ex/mt/data/labse1",
               block=8,
               min_socre=0.6,
               clean_after_done=False,
               logger=None):
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
    out_path = os.path.join(filter_dir, path + ".sf")
    if not os.path.exists(out_path):
        path = merge(filter_dir, out_path, clean_after_merge=clean_after_done, logger_opus=logger)

    return path


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--input", required=True,  help="Root dir")
    argparser.add_argument("--labse", default="D:/kidden/mt/open/mt-ex/mt/data/labse1", help="directory for labse")
    argparser.add_argument("--block", type=int, default=8, help="block size for labse")
    argparser.add_argument("--min", type=float, default=0.6, help="min socre for filtering")
    argparser.add_argument("--log_dir", default="./", help="log directory")
    args = argparser.parse_args()

    logger_opus = get_logger(os.path.join(args.log_dir, "opus.log"), "OPUS")

    p = args.input
    score_and_filter(p, labse_model_dir=args.labse, block=args.block, min_socre=args.min,
                   clean_after_done=False, logger=logger_opus)
