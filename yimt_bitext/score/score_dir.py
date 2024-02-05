import os
import re
from argparse import ArgumentParser

from yimt_bitext.score.score_bitext import score_tsv
from yimt_bitext.utils.log import get_logger

if __name__ == "__main__":
    argparser = ArgumentParser(description="Scoring corpus")
    argparser.add_argument("--input", required=True,  help="Input directory")
    argparser.add_argument("--labse", default="D:/kidden/mt/open/mt-ex/mt/data/labse1", help="directory for labse")
    argparser.add_argument("--block", type=int, default=8, help="block size for labse")
    argparser.add_argument("--log_dir", default="./", help="log directory")
    args = argparser.parse_args()

    logger_opus = get_logger(os.path.join(args.log_dir, "opus.log"), "OPUS")

    p = args.input
    files = os.listdir(p)
    for f in files:
        if re.match(r".+\d+$", f):
            in_path = os.path.join(p, f)
            out_path = in_path + ".score"

            if os.path.exists(out_path):
                logger_opus.info("{} exists".format(out_path))
                continue

            score_tsv(in_path, labse_model_dir=args.labse,
                      block=args.block, logger=logger_opus)